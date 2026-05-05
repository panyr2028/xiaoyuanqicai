# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
出入库管理模块
"""

from datetime import datetime
import config
from database import get_db
from logger import log_info, log_error, log_operation
from equipment import EquipmentManager


class InOutManager:
    """出入库管理类"""

    @staticmethod
    def generate_record_no():
        """生成记录编号"""
        today = datetime.now().strftime('%Y%m%d')
        timestamp = datetime.now().strftime('%H%M%S')
        return f"IO{today}{timestamp}"

    @staticmethod
    def stock_in(equipment_id, quantity, purpose, remarks, operator_id, operator_name):
        """器材入库"""
        db = get_db()

        equipment = EquipmentManager.get_equipment_by_id(equipment_id)
        if not equipment:
            return False, "器材不存在"

        if quantity <= 0:
            return False, "入库数量必须大于零"

        before_quantity = equipment['quantity']
        after_quantity = before_quantity + quantity

        # 生成记录编号
        record_no = InOutManager.generate_record_no()

        # 插入入库记录
        insert_sql = """
        INSERT INTO in_out_record (
            record_no, equipment_id, equipment_code, equipment_name, equipment_type,
            record_type, quantity, before_quantity, after_quantity,
            operator_id, operator_name, purpose, remarks
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            with db.get_cursor() as cursor:
                cursor.execute(insert_sql, (
                    record_no, equipment_id, equipment['equipment_code'],
                    equipment['name'], equipment['type'],
                    'in', quantity, before_quantity, after_quantity,
                    operator_id, operator_name, purpose, remarks
                ))

                # 更新器材库存
                update_sql = "UPDATE equipment SET quantity = ?, updated_at = ? WHERE id = ?"
                cursor.execute(update_sql, (after_quantity, datetime.now(), equipment_id))

            log_info(f"器材 {equipment['equipment_code']} 入库成功: +{quantity}")
            log_operation(operator_id, operator_name, 'stock_in', 'in_out',
                          f'器材入库: {equipment["equipment_code"]} +{quantity}')

            return True, "入库成功"

        except Exception as e:
            log_error(f"器材入库失败: {e}")
            return False, f"入库失败: {str(e)}"

    @staticmethod
    def stock_out(equipment_id, quantity, purpose, remarks, operator_id, operator_name):
        """器材出库"""
        db = get_db()

        equipment = EquipmentManager.get_equipment_by_id(equipment_id)
        if not equipment:
            return False, "器材不存在"

        if quantity <= 0:
            return False, "出库数量必须大于零"

        before_quantity = equipment['quantity']

        if before_quantity < quantity:
            return False, f"库存不足，当前库存: {before_quantity}"

        after_quantity = before_quantity - quantity

        # 生成记录编号
        record_no = InOutManager.generate_record_no()

        # 插入出库记录
        insert_sql = """
        INSERT INTO in_out_record (
            record_no, equipment_id, equipment_code, equipment_name, equipment_type,
            record_type, quantity, before_quantity, after_quantity,
            operator_id, operator_name, purpose, remarks
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            with db.get_cursor() as cursor:
                cursor.execute(insert_sql, (
                    record_no, equipment_id, equipment['equipment_code'],
                    equipment['name'], equipment['type'],
                    'out', quantity, before_quantity, after_quantity,
                    operator_id, operator_name, purpose, remarks
                ))

                # 更新器材库存
                update_sql = "UPDATE equipment SET quantity = ?, updated_at = ? WHERE id = ?"
                cursor.execute(update_sql, (after_quantity, datetime.now(), equipment_id))

            log_info(f"器材 {equipment['equipment_code']} 出库成功: -{quantity}")
            log_operation(operator_id, operator_name, 'stock_out', 'in_out',
                          f'器材出库: {equipment["equipment_code"]} -{quantity}')

            return True, "出库成功"

        except Exception as e:
            log_error(f"器材出库失败: {e}")
            return False, f"出库失败: {str(e)}"

    @staticmethod
    def get_records(page=1, page_size=20, equipment_type=None, record_type=None,
                    start_date=None, end_date=None, keyword=''):
        """获取出入库记录"""
        db = get_db()
        offset = (page - 1) * page_size

        sql = "SELECT * FROM in_out_record WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM in_out_record WHERE 1=1"
        params = []
        count_params = []

        if equipment_type:
            sql += " AND equipment_type = ?"
            count_sql += " AND equipment_type = ?"
            params.append(equipment_type)
            count_params.append(equipment_type)

        if record_type:
            sql += " AND record_type = ?"
            count_sql += " AND record_type = ?"
            params.append(record_type)
            count_params.append(record_type)

        if start_date:
            sql += " AND operate_time >= ?"
            count_sql += " AND operate_time >= ?"
            params.append(start_date)
            count_params.append(start_date)

        if end_date:
            sql += " AND operate_time <= ?"
            count_sql += " AND operate_time <= ?"
            params.append(end_date)
            count_params.append(end_date)

        if keyword:
            sql += " AND (equipment_code LIKE ? OR equipment_name LIKE ? OR record_no LIKE ?)"
            count_sql += " AND (equipment_code LIKE ? OR equipment_name LIKE ? OR record_no LIKE ?)"
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
            count_params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

        sql += " ORDER BY operate_time DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        records = db.fetchall(sql, params)
        total_result = db.fetchone(count_sql, count_params)
        total = total_result['total'] if total_result else 0

        return [dict(record) for record in records], total

    @staticmethod
    def get_record_by_id(record_id):
        """根据ID获取记录"""
        db = get_db()
        sql = "SELECT * FROM in_out_record WHERE id = ?"
        result = db.fetchone(sql, (record_id,))
        return dict(result) if result else None

    @staticmethod
    def get_record_statistics(start_date=None, end_date=None, equipment_type=None):
        """获取出入库统计"""
        db = get_db()

        sql = """
        SELECT
            record_type,
            COUNT(*) as count,
            SUM(quantity) as total_quantity,
            equipment_type
        FROM in_out_record WHERE 1=1
        """
        params = []

        if start_date:
            sql += " AND operate_time >= ?"
            params.append(start_date)

        if end_date:
            sql += " AND operate_time <= ?"
            params.append(end_date)

        if equipment_type:
            sql += " AND equipment_type = ?"
            params.append(equipment_type)

        sql += " GROUP BY record_type, equipment_type"

        results = db.fetchall(sql, params)

        statistics = {}
        for result in results:
            record_type = result['record_type']
            if record_type not in statistics:
                statistics[record_type] = {
                    'count': 0,
                    'total_quantity': 0,
                    'by_type': {}
                }

            statistics[record_type]['count'] += result['count']
            statistics[record_type]['total_quantity'] += result['total_quantity']
            statistics[record_type]['by_type'][result['equipment_type']] = {
                'count': result['count'],
                'quantity': result['total_quantity']
            }

        return statistics

    @staticmethod
    def get_recent_records(limit=10):
        """获取最近的出入库记录"""
        db = get_db()
        sql = "SELECT * FROM in_out_record ORDER BY operate_time DESC LIMIT ?"
        results = db.fetchall(sql, (limit,))
        return [dict(record) for record in results]

    @staticmethod
    def cancel_record(record_id, operator_id, operator_name, reason):
        """撤销出入库记录"""
        db = get_db()

        record = InOutManager.get_record_by_id(record_id)
        if not record:
            return False, "记录不存在"

        if record['record_type'] == 'in':
            quantity_change = -record['quantity']
            action_desc = f"撤销入库: {record['equipment_code']} -{record['quantity']}"
        else:
            quantity_change = record['quantity']
            action_desc = f"撤销出库: {record['equipment_code']} +{record['quantity']}"

        try:
            with db.get_cursor() as cursor:
                # 恢复器材库存
                equipment = EquipmentManager.get_equipment_by_id(record['equipment_id'])
                new_quantity = equipment['quantity'] + quantity_change

                update_sql = "UPDATE equipment SET quantity = ?, updated_at = ? WHERE id = ?"
                cursor.execute(update_sql, (new_quantity, datetime.now(), record['equipment_id']))

                # 删除记录
                delete_sql = "DELETE FROM in_out_record WHERE id = ?"
                cursor.execute(delete_sql, (record_id,))

            log_info(f"撤销记录成功: {record_id}")
            log_operation(operator_id, operator_name, 'cancel_record', 'in_out',
                          f'{action_desc}, 原因: {reason}')

            return True, "撤销成功"

        except Exception as e:
            log_error(f"撤销记录失败: {e}")
            return False, f"撤销失败: {str(e)}"
