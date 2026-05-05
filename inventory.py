# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
库存管理模块
"""

from datetime import datetime
import config
from database import get_db
from logger import log_info, log_error, log_operation
from equipment import EquipmentManager


class InventoryManager:
    """库存管理类"""

    @staticmethod
    def get_inventory_summary():
        """获取库存汇总信息"""
        db = get_db()

        sql = """
        SELECT
            type,
            COUNT(*) as equipment_count,
            SUM(quantity) as total_quantity
        FROM equipment
        WHERE status = 1
        GROUP BY type
        """

        results = db.fetchall(sql)

        summary = {}
        for result in results:
            summary[result['type']] = {
                'equipment_count': result['equipment_count'],
                'total_quantity': result['total_quantity']
            }

        # 计算总计
        total_sql = "SELECT SUM(quantity) as total FROM equipment WHERE status = 1"
        total_result = db.fetchone(total_sql)
        summary['total'] = total_result['total'] if total_result and total_result['total'] else 0

        return summary

    @staticmethod
    def inventory_check(equipment_id, actual_quantity, check_type, checker_id, checker_name, remarks=''):
        """库存盘点"""
        db = get_db()

        equipment = EquipmentManager.get_equipment_by_id(equipment_id)
        if not equipment:
            return False, "器材不存在"

        system_quantity = equipment['quantity']
        difference = actual_quantity - system_quantity

        # 生成盘点编号
        today = datetime.now().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        check_no = f"IC{today}{timestamp}"

        insert_sql = """
        INSERT INTO inventory_check (
            check_no, equipment_id, equipment_code, equipment_name,
            system_quantity, actual_quantity, difference,
            check_type, checker_id, checker_name, remarks
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            with db.get_cursor() as cursor:
                cursor.execute(insert_sql, (
                    check_no, equipment_id, equipment['equipment_code'],
                    equipment['name'], system_quantity, actual_quantity, difference,
                    check_type, checker_id, checker_name, remarks
                ))

                # 如果有差异，更新系统库存
                if difference != 0:
                    update_sql = "UPDATE equipment SET quantity = ?, updated_at = ? WHERE id = ?"
                    cursor.execute(update_sql, (actual_quantity, datetime.now(), equipment_id))

            action_desc = f"库存盘点: {equipment['equipment_code']}, 系统:{system_quantity}, 实际:{actual_quantity}, 差异:{difference}"
            log_info(action_desc)
            log_operation(checker_id, checker_name, 'inventory_check', 'inventory', action_desc)

            return True, f"盘点完成，差异: {difference}"

        except Exception as e:
            log_error(f"库存盘点失败: {e}")
            return False, f"盘点失败: {str(e)}"

    @staticmethod
    def get_check_records(page=1, page_size=20, equipment_type=None, start_date=None, end_date=None):
        """获取盘点记录"""
        db = get_db()
        offset = (page - 1) * page_size

        sql = "SELECT * FROM inventory_check WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM inventory_check WHERE 1=1"
        params = []
        count_params = []

        if equipment_type:
            sql = """
            SELECT ic.* FROM inventory_check ic
            JOIN equipment e ON ic.equipment_id = e.id
            WHERE e.type = ?
            """
            count_sql = """
            SELECT COUNT(*) as total FROM inventory_check ic
            JOIN equipment e ON ic.equipment_id = e.id
            WHERE e.type = ?
            """
            params.append(equipment_type)
            count_params.append(equipment_type)

        if start_date:
            sql += " AND check_time >= ?" if not equipment_type else " AND ic.check_time >= ?"
            count_sql += " AND check_time >= ?" if not equipment_type else " AND ic.check_time >= ?"
            params.append(start_date)
            count_params.append(start_date)

        if end_date:
            sql += " AND check_time <= ?" if not equipment_type else " AND ic.check_time <= ?"
            count_sql += " AND check_time <= ?" if not equipment_type else " AND ic.check_time <= ?"
            params.append(end_date)
            count_params.append(end_date)

        sql += " ORDER BY check_time DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        records = db.fetchall(sql, params)
        total_result = db.fetchone(count_sql, count_params)
        total = total_result['total'] if total_result else 0

        return [dict(r) for r in records], total

    @staticmethod
    def inventory_adjustment(equipment_id, new_quantity, reason, operator_id, operator_name):
        """库存调整"""
        db = get_db()

        equipment = EquipmentManager.get_equipment_by_id(equipment_id)
        if not equipment:
            return False, "器材不存在"

        old_quantity = equipment['quantity']
        difference = new_quantity - old_quantity

        try:
            with db.get_cursor() as cursor:
                # 更新器材库存
                update_sql = "UPDATE equipment SET quantity = ?, updated_at = ? WHERE id = ?"
                cursor.execute(update_sql, (new_quantity, datetime.now(), equipment_id))

                # 生成记录编号
                today = datetime.now().strftime('%Y%m%d')
                timestamp = datetime.now().strftime('%H%M%S')
                record_no = f"IA{today}{timestamp}"

                # 记录调整
                record_sql = """
                INSERT INTO in_out_record (
                    record_no, equipment_id, equipment_code, equipment_name, equipment_type,
                    record_type, quantity, before_quantity, after_quantity,
                    operator_id, operator_name, purpose, remarks
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(record_sql, (
                    record_no, equipment_id, equipment['equipment_code'],
                    equipment['name'], equipment['type'],
                    'adjust', abs(difference), old_quantity, new_quantity,
                    operator_id, operator_name, '库存调整', reason
                ))

            action_desc = f"库存调整: {equipment['equipment_code']}, {old_quantity} -> {new_quantity}, 原因: {reason}"
            log_info(action_desc)
            log_operation(operator_id, operator_name, 'adjust', 'inventory', action_desc)

            return True, f"调整成功，差异: {difference:+d}"

        except Exception as e:
            log_error(f"库存调整失败: {e}")
            return False, f"调整失败: {str(e)}"

    @staticmethod
    def get_inventory_details(equipment_type=None):
        """获取库存明细"""
        db = get_db()

        sql = """
        SELECT e.*,
               COALESCE(SUM(CASE WHEN ior.record_type = 'in' THEN ior.quantity ELSE 0 END), 0) as total_in,
               COALESCE(SUM(CASE WHEN ior.record_type = 'out' THEN ior.quantity ELSE 0 END), 0) as total_out
        FROM equipment e
        LEFT JOIN in_out_record ior ON e.id = ior.equipment_id
        WHERE e.status = 1
        """

        params = []
        if equipment_type:
            sql += " AND e.type = ?"
            params.append(equipment_type)

        sql += " GROUP BY e.id ORDER BY e.type, e.equipment_code"

        results = db.fetchall(sql, params)
        return [dict(r) for r in results]
