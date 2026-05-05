# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
器材信息管理模块
"""

from datetime import datetime
import config
from database import get_db
from logger import log_info, log_error, log_operation


class EquipmentManager:
    """器材信息管理类"""

    @staticmethod
    def generate_equipment_code(equipment_type):
        """生成器材编号"""
        type_prefix_map = {
            'basketball': 'BB',
            'volleyball': 'VB',
            'badminton_racket': 'BR',
            'pingpong_racket': 'PR',
            'tennis_racket': 'TR'
        }
        prefix = type_prefix_map.get(equipment_type, 'EQ')

        db = get_db()
        today = datetime.now().strftime('%Y%m%d')

        sql = "SELECT equipment_code FROM equipment WHERE equipment_code LIKE ? ORDER BY id DESC LIMIT 1"
        result = db.fetchone(sql, (f"{prefix}{today}%",))

        if result:
            last_seq = int(result['equipment_code'][-4:])
            new_seq = last_seq + 1
        else:
            new_seq = 1

        return f"{prefix}{today}{new_seq:04d}"

    @staticmethod
    def add_equipment(equipment_code, name, equipment_type, specification, quantity, unit,
                      purchase_date, supplier, purchase_price, remarks, created_by):
        """添加器材"""
        db = get_db()

        # 检查器材编号是否已存在
        check_sql = "SELECT id FROM equipment WHERE equipment_code = ?"
        if db.fetchone(check_sql, (equipment_code,)):
            return False, "器材编号已存在"

        insert_sql = """
        INSERT INTO equipment (
            equipment_code, name, type, specification, quantity, unit,
            purchase_date, supplier, purchase_price, remarks, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            db.execute(insert_sql, (
                equipment_code, name, equipment_type, specification, quantity, unit,
                purchase_date, supplier, purchase_price, remarks, created_by
            ))
            log_info(f"添加器材成功: {equipment_code} - {name}")
            log_operation(created_by, '', 'add', 'equipment', f'添加器材: {equipment_code} - {name}')
            return True, "添加成功"
        except Exception as e:
            log_error(f"添加器材失败: {e}")
            return False, f"添加失败: {str(e)}"

    @staticmethod
    def update_equipment(equipment_id, name=None, specification=None, supplier=None,
                        purchase_price=None, remarks=None, status=None):
        """更新器材信息"""
        db = get_db()

        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if specification is not None:
            updates.append("specification = ?")
            params.append(specification)
        if supplier is not None:
            updates.append("supplier = ?")
            params.append(supplier)
        if purchase_price is not None:
            updates.append("purchase_price = ?")
            params.append(purchase_price)
        if remarks is not None:
            updates.append("remarks = ?")
            params.append(remarks)
        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if not updates:
            return False, "没有需要更新的字段"

        updates.append("updated_at = ?")
        params.append(datetime.now())
        params.append(equipment_id)

        sql = f"UPDATE equipment SET {', '.join(updates)} WHERE id = ?"

        try:
            db.execute(sql, params)
            log_info(f"器材ID {equipment_id} 信息已更新")
            return True, "更新成功"
        except Exception as e:
            log_error(f"更新器材信息失败: {e}")
            return False, f"更新失败: {str(e)}"

    @staticmethod
    def delete_equipment(equipment_id, user_id):
        """删除器材"""
        db = get_db()

        # 检查器材是否有未处理的出入库记录
        check_sql = "SELECT COUNT(*) as count FROM in_out_record WHERE equipment_id = ?"
        result = db.fetchone(check_sql, (equipment_id,))
        if result and result['count'] > 0:
            return False, "该器材存在出入库记录，无法删除"

        # 检查器材库存是否为零
        equipment = EquipmentManager.get_equipment_by_id(equipment_id)
        if equipment and equipment['quantity'] > 0:
            return False, "该器材库存不为零，无法删除"

        sql = "DELETE FROM equipment WHERE id = ?"
        try:
            db.execute(sql, (equipment_id,))
            log_info(f"器材ID {equipment_id} 已删除")
            log_operation(user_id, '', 'delete', 'equipment', f'删除器材ID: {equipment_id}')
            return True, "删除成功"
        except Exception as e:
            log_error(f"删除器材失败: {e}")
            return False, f"删除失败: {str(e)}"

    @staticmethod
    def get_equipment_by_id(equipment_id):
        """根据ID获取器材信息"""
        db = get_db()
        sql = "SELECT * FROM equipment WHERE id = ?"
        result = db.fetchone(sql, (equipment_id,))
        return dict(result) if result else None

    @staticmethod
    def get_equipment_by_code(equipment_code):
        """根据编号获取器材信息"""
        db = get_db()
        sql = "SELECT * FROM equipment WHERE equipment_code = ?"
        result = db.fetchone(sql, (equipment_code,))
        return dict(result) if result else None

    @staticmethod
    def get_all_equipments(page=1, page_size=20, equipment_type=None, keyword='', status=1):
        """获取器材列表"""
        db = get_db()
        offset = (page - 1) * page_size

        sql = "SELECT * FROM equipment WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM equipment WHERE 1=1"
        params = []
        count_params = []

        if status is not None:
            sql += " AND status = ?"
            count_sql += " AND status = ?"
            params.append(status)
            count_params.append(status)

        if equipment_type:
            sql += " AND type = ?"
            count_sql += " AND type = ?"
            params.append(equipment_type)
            count_params.append(equipment_type)

        if keyword:
            sql += " AND (equipment_code LIKE ? OR name LIKE ? OR supplier LIKE ?)"
            count_sql += " AND (equipment_code LIKE ? OR name LIKE ? OR supplier LIKE ?)"
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
            count_params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        equipments = db.fetchall(sql, params)
        total_result = db.fetchone(count_sql, count_params)
        total = total_result['total'] if total_result else 0

        return [dict(eq) for eq in equipments], total

    @staticmethod
    def get_equipment_statistics():
        """获取器材统计信息"""
        db = get_db()
        statistics = {}

        # 按类型统计
        type_sql = """
        SELECT type, COUNT(*) as count, SUM(quantity) as total_quantity
        FROM equipment WHERE status = 1 GROUP BY type
        """
        type_results = db.fetchall(type_sql)

        for result in type_results:
            statistics[result['type']] = {
                'count': result['count'],
                'total_quantity': result['total_quantity']
            }

        # 总数统计
        total_sql = "SELECT COUNT(*) as total_count, SUM(quantity) as total FROM equipment WHERE status = 1"
        total_result = db.fetchone(total_sql)
        statistics['total'] = {
            'count': total_result['total_count'] if total_result else 0,
            'quantity': total_result['total'] if total_result else 0
        }

        return statistics

    @staticmethod
    def update_quantity(equipment_id, quantity_change, operator_id, operator_name):
        """更新器材库存数量"""
        db = get_db()

        equipment = EquipmentManager.get_equipment_by_id(equipment_id)
        if not equipment:
            return False, "器材不存在"

        new_quantity = equipment['quantity'] + quantity_change
        if new_quantity < 0:
            return False, "库存不足"

        update_sql = "UPDATE equipment SET quantity = ?, updated_at = ? WHERE id = ?"
        db.execute(update_sql, (new_quantity, datetime.now(), equipment_id))

        log_info(f"器材 {equipment['equipment_code']} 库存更新: {equipment['quantity']} -> {new_quantity}")

        return True, new_quantity

    @staticmethod
    def get_specification_details_by_type(equipment_type, detail_type='stock'):
        """根据器材类型获取不同规格的详细信息"""
        db = get_db()
        
        if detail_type == 'asset':
            sql = """
            SELECT e.specification, COALESCE(SUM(r.quantity), 0) as asset_total
            FROM equipment e
            LEFT JOIN in_out_record r ON e.id = r.equipment_id AND r.record_type = 'in'
            WHERE e.type = ? AND e.status = 1
            GROUP BY e.specification
            ORDER BY e.specification
            """
            results = db.fetchall(sql, (equipment_type,))
            return [dict(row) for row in results]
        else:
            sql = """
            SELECT specification, SUM(quantity) as total_quantity
            FROM equipment 
            WHERE type = ? AND status = 1 
            GROUP BY specification 
            ORDER BY specification
            """
            results = db.fetchall(sql, (equipment_type,))
            return [dict(row) for row in results]
    

