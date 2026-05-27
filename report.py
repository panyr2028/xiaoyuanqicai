# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
数据查询与统计模块
"""

from datetime import datetime, timedelta
import os
import csv
import config
from database import get_db
from logger import log_info, log_error


class ReportManager:
    """报表管理类"""

    @staticmethod
    def get_dashboard_data():
        """获取仪表盘数据"""
        db = get_db()
        dashboard = {}

        # 今日入库
        today_start = datetime.now().strftime('%Y-%m-%d 00:00:00')
        today_end = datetime.now().strftime('%Y-%m-%d 23:59:59')
        in_today_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE record_type = 'in' AND operate_time >= ? AND operate_time <= ?
        """
        in_today = db.fetchone(in_today_sql, (today_start, today_end))
        dashboard['today_in'] = {
            'count': in_today['count'] if in_today else 0,
            'quantity': in_today['quantity'] if in_today else 0
        }

        # 今日出库
        out_today_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE record_type = 'out' AND operate_time >= ? AND operate_time <= ?
        """
        out_today = db.fetchone(out_today_sql, (today_start, today_end))
        dashboard['today_out'] = {
            'count': out_today['count'] if out_today else 0,
            'quantity': out_today['quantity'] if out_today else 0
        }

        # 器材总数（各类器材入库+出库累计总和）
        total_in_sql = "SELECT COALESCE(SUM(quantity), 0) as total FROM in_out_record WHERE record_type = 'in'"
        total_out_sql = "SELECT COALESCE(SUM(quantity), 0) as total FROM in_out_record WHERE record_type = 'out'"
        total_in = db.fetchone(total_in_sql)['total'] or 0
        total_out = db.fetchone(total_out_sql)['total'] or 0
        total_count = total_in + total_out
        dashboard['total_equipment'] = {
            'count': total_count,
            'quantity': total_count
        }

        # 器材库存统计（所有器材的库存之和）
        inventory_total_sql = "SELECT COALESCE(SUM(quantity), 0) as total FROM equipment WHERE status = 1"
        inventory_result = db.fetchone(inventory_total_sql)
        dashboard['inventory_total'] = {
            'count': inventory_result['total'] if inventory_result else 0,
            'quantity': inventory_result['total'] if inventory_result else 0
        }

        # 库存预警数（已去除，设为0）
        dashboard['warning_count'] = 0

        # 各类型器材库存
        type_summary = {}
        # 各类型器材资产总数（累计入库数量）
        type_asset_total = {}
        for equip_type, type_name in config.EQUIPMENT_TYPES:
            # 库存数量
            sql = """
            SELECT COALESCE(SUM(quantity), 0) as quantity
            FROM equipment WHERE type = ? AND status = 1
            """
            result = db.fetchone(sql, (equip_type,))
            # 资产总数（累计入库数量）
            asset_sql = """
            SELECT COALESCE(SUM(quantity), 0) as total
            FROM in_out_record 
            WHERE record_type = 'in' AND equipment_type = ?
            """
            asset_result = db.fetchone(asset_sql, (equip_type,))
            type_summary[equip_type] = {
                'quantity': result['quantity'] if result else 0,
                'asset_total': asset_result['total'] if asset_result else 0
            }
            type_asset_total[equip_type] = asset_result['total'] if asset_result else 0
        
        dashboard['type_summary'] = type_summary
        dashboard['type_asset_total'] = type_asset_total

        # 最近操作记录（保留但不使用）
        recent_sql = """
        SELECT * FROM in_out_record 
        ORDER BY operate_time DESC LIMIT 10
        """
        recent_records = db.fetchall(recent_sql)
        dashboard['recent_records'] = [dict(r) for r in recent_records]

        return dashboard

    @staticmethod
    def get_dashboard_data_old():
        """获取仪表盘数据（旧版，保留兼容）"""
        db = get_db()
        dashboard = {}

        # 今日入库
        today_start = datetime.now().strftime('%Y-%m-%d 00:00:00')
        today_end = datetime.now().strftime('%Y-%m-%d 23:59:59')
        in_today_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE record_type = 'in' AND operate_time >= ? AND operate_time <= ?
        """
        in_today = db.fetchone(in_today_sql, (today_start, today_end))
        dashboard['today_in'] = {
            'count': in_today['count'] if in_today else 0,
            'quantity': in_today['quantity'] if in_today else 0
        }

        # 今日出库
        out_today_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE record_type = 'out' AND operate_time >= ? AND operate_time <= ?
        """
        out_today = db.fetchone(out_today_sql, (today_start, today_end))
        dashboard['today_out'] = {
            'count': out_today['count'] if out_today else 0,
            'quantity': out_today['quantity'] if out_today else 0
        }

        # 器材总数（各类器材入库+出库累计总和）
        total_in_sql = "SELECT COALESCE(SUM(quantity), 0) as total FROM in_out_record WHERE record_type = 'in'"
        total_out_sql = "SELECT COALESCE(SUM(quantity), 0) as total FROM in_out_record WHERE record_type = 'out'"
        total_in = db.fetchone(total_in_sql)['total'] or 0
        total_out = db.fetchone(total_out_sql)['total'] or 0
        total_count = total_in + total_out
        dashboard['total_equipment'] = {
            'count': total_count,
            'quantity': total_count
        }

        # 器材库存统计（所有器材的库存之和）
        inventory_total_sql = "SELECT COALESCE(SUM(quantity), 0) as total FROM equipment WHERE status = 1"
        inventory_result = db.fetchone(inventory_total_sql)
        dashboard['inventory_total'] = {
            'count': inventory_result['total'] if inventory_result else 0,
            'quantity': inventory_result['total'] if inventory_result else 0
        }

        # 库存预警数（已去除，设为0）
        dashboard['warning_count'] = 0

        # 各类型器材库存（旧版）
        type_summary = {}
        for equip_type, type_name in config.EQUIPMENT_TYPES:
            sql = """
            SELECT COALESCE(SUM(quantity), 0) as quantity
            FROM equipment WHERE type = ? AND status = 1
            """
            result = db.fetchone(sql, (equip_type,))
            type_summary[equip_type] = {
                'name': type_name,
                'quantity': result['quantity'] if result else 0
            }
        dashboard['type_summary'] = type_summary

        # 最近操作记录
        recent_sql = "SELECT * FROM in_out_record ORDER BY operate_time DESC LIMIT 10"
        recent_records = db.fetchall(recent_sql)
        dashboard['recent_records'] = [dict(r) for r in recent_records]

        # 本月出入库统计
        month_start = datetime.now().strftime('%Y-%m-01 00:00:00')
        month_in_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record WHERE record_type = 'in' AND operate_time >= ?
        """
        month_out_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record WHERE record_type = 'out' AND operate_time >= ?
        """
        month_in = db.fetchone(month_in_sql, (month_start,))
        month_out = db.fetchone(month_out_sql, (month_start,))
        dashboard['month_stats'] = {
            'in_count': month_in['count'] if month_in else 0,
            'in_quantity': month_in['quantity'] if month_in else 0,
            'out_count': month_out['count'] if month_out else 0,
            'out_quantity': month_out['quantity'] if month_out else 0
        }

        return dashboard

    @staticmethod
    def query_equipment(equipment_type=None, keyword='', start_date=None, end_date=None,
                        supplier='', status=1):
        """多条件查询器材"""
        db = get_db()

        sql = "SELECT * FROM equipment WHERE 1=1"
        params = []

        if status is not None:
            sql += " AND status = ?"
            params.append(status)

        if equipment_type:
            sql += " AND type = ?"
            params.append(equipment_type)

        if keyword:
            sql += " AND (equipment_code LIKE ? OR name LIKE ?)"
            params.append(f"%{keyword}%")
            params.append(f"%{keyword}%")

        if start_date:
            sql += " AND purchase_date >= ?"
            params.append(start_date)

        if end_date:
            sql += " AND purchase_date <= ?"
            params.append(end_date)

        if supplier:
            sql += " AND supplier LIKE ?"
            params.append(f"%{supplier}%")

        sql += " ORDER BY created_at DESC"

        results = db.fetchall(sql, params)
        return [dict(r) for r in results]

    @staticmethod
    def query_records(record_type=None, equipment_type=None, keyword='',
                      start_date=None, end_date=None):
        """多条件查询出入库记录"""
        db = get_db()

        sql = "SELECT * FROM in_out_record WHERE 1=1"
        params = []

        if record_type:
            sql += " AND record_type = ?"
            params.append(record_type)

        if equipment_type:
            sql += " AND equipment_type = ?"
            params.append(equipment_type)

        if keyword:
            sql += " AND (equipment_code LIKE ? OR equipment_name LIKE ? OR record_no LIKE ?)"
            params.append(f"%{keyword}%")
            params.append(f"%{keyword}%")
            params.append(f"%{keyword}%")

        if start_date:
            sql += " AND operate_time >= ?"
            params.append(start_date)

        if end_date:
            sql += " AND operate_time <= ?"
            params.append(end_date)

        sql += " ORDER BY operate_time DESC"

        results = db.fetchall(sql, params)
        return [dict(r) for r in results]

    @staticmethod
    def generate_daily_report(date=None):
        """生成日报"""
        if date is None:
            date = datetime.now()

        date_str = date.strftime('%Y-%m-%d')
        start_time = f"{date_str} 00:00:00"
        end_time = f"{date_str} 23:59:59"

        db = get_db()

        # 入库统计
        in_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE record_type = 'in' AND operate_time >= ? AND operate_time <= ?
        """
        in_result = db.fetchone(in_sql, (start_time, end_time))

        # 出库统计
        out_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE record_type = 'out' AND operate_time >= ? AND operate_time <= ?
        """
        out_result = db.fetchone(out_sql, (start_time, end_time))

        # 详细记录
        detail_sql = """
        SELECT * FROM in_out_record
        WHERE operate_time >= ? AND operate_time <= ?
        ORDER BY operate_time DESC
        """
        detail_records = db.fetchall(detail_sql, (start_time, end_time))

        # 各类型统计
        type_sql = """
        SELECT equipment_type, record_type, COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE operate_time >= ? AND operate_time <= ?
        GROUP BY equipment_type, record_type
        """
        type_results = db.fetchall(type_sql, (start_time, end_time))

        report = {
            'date': date_str,
            'in_summary': {
                'count': in_result['count'] if in_result else 0,
                'quantity': in_result['quantity'] if in_result else 0
            },
            'out_summary': {
                'count': out_result['count'] if out_result else 0,
                'quantity': out_result['quantity'] if out_result else 0
            },
            'detail_records': [dict(r) for r in detail_records],
            'type_statistics': [dict(r) for r in type_results]
        }

        return report

    @staticmethod
    def generate_monthly_report(year=None, month=None):
        """生成月报"""
        if year is None or month is None:
            now = datetime.now()
            year = now.year
            month = now.month

        start_date = f"{year}-{month:02d}-01 00:00:00"
        if month == 12:
            end_date = f"{year + 1}-01-01 00:00:00"
        else:
            end_date = f"{year}-{month + 1:02d}-01 00:00:00"

        db = get_db()

        # 入库统计
        in_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE record_type = 'in' AND operate_time >= ? AND operate_time < ?
        """
        in_result = db.fetchone(in_sql, (start_date, end_date))

        # 出库统计
        out_sql = """
        SELECT COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE record_type = 'out' AND operate_time >= ? AND operate_time < ?
        """
        out_result = db.fetchone(out_sql, (start_date, end_date))

        # 各类型月度统计
        type_sql = """
        SELECT equipment_type, record_type, COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE operate_time >= ? AND operate_time < ?
        GROUP BY equipment_type, record_type
        """
        type_results = db.fetchall(type_sql, (start_date, end_date))

        # 日统计
        daily_sql = """
        SELECT DATE(operate_time) as date, record_type, SUM(quantity) as quantity
        FROM in_out_record
        WHERE operate_time >= ? AND operate_time < ?
        GROUP BY DATE(operate_time), record_type
        ORDER BY date
        """
        daily_results = db.fetchall(daily_sql, (start_date, end_date))

        report = {
            'year': year,
            'month': month,
            'in_summary': {
                'count': in_result['count'] if in_result else 0,
                'quantity': in_result['quantity'] if in_result else 0
            },
            'out_summary': {
                'count': out_result['count'] if out_result else 0,
                'quantity': out_result['quantity'] if out_result else 0
            },
            'type_statistics': [dict(r) for r in type_results],
            'daily_statistics': [dict(r) for r in daily_results]
        }

        return report

    @staticmethod
    def export_to_csv(data, filename, headers):
        export_dir = os.path.join(config.BASE_DIR, config.EXPORT_CONFIG['export_dir'])
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        filepath = os.path.join(export_dir, filename)

        try:
            with open(filepath, 'w', newline='', encoding=config.EXPORT_CONFIG['csv_encoding']) as f:
                writer = csv.writer(f)
                writer.writerow(headers)

                for row in data:
                    if isinstance(row, dict):
                        writer.writerow([row.get(h, '') for h in headers])
                    else:
                        writer.writerow(row)

            log_info(f"数据已导出到CSV: {filepath}")
            return filepath
        except Exception as e:
            log_error(f"导出CSV失败: {e}")
            return None

    @staticmethod
    def export_equipment_report(equipment_type=None, keyword='', start_date=None, end_date=None):
        data = ReportManager.query_equipment(equipment_type, keyword, start_date, end_date)

        headers = ['器材编号', '名称', '类型', '规格', '数量', '单位', '采购日期', '供应商', '采购价格', '状态']
        filename = f"器材报表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return ReportManager.export_to_csv(data, filename, headers)

    @staticmethod
    def export_record_report(record_type=None, equipment_type=None, keyword='',
                             start_date=None, end_date=None):
        data = ReportManager.query_records(record_type, equipment_type, keyword, start_date, end_date)

        headers = ['记录编号', '器材编号', '器材名称', '器材类型', '操作类型', '数量', '操作前库存',
                   '操作后库存', '操作人', '操作时间', '用途', '备注']
        filename = f"出入库记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return ReportManager.export_to_csv(data, filename, headers)

    @staticmethod
    def get_statistics_by_date(start_date, end_date):
        db = get_db()

        end_datetime = f"{end_date} 23:59:59"

        sql = """
        SELECT DATE(operate_time) as date, record_type,
               COUNT(*) as count, SUM(quantity) as quantity
        FROM in_out_record
        WHERE operate_time >= ? AND operate_time <= ?
        GROUP BY DATE(operate_time), record_type
        ORDER BY date
        """

        results = db.fetchall(sql, (start_date, end_datetime))

        statistics = {}
        for r in results:
            date_str = r['date']
            if date_str not in statistics:
                statistics[date_str] = {'in': {'count': 0, 'quantity': 0}, 'out': {'count': 0, 'quantity': 0}}

            record_type = r['record_type']
            statistics[date_str][record_type] = {
                'count': r['count'],
                'quantity': r['quantity']
            }

        return statistics

    @staticmethod
    def get_equipment_trend(equipment_id, days=30):
        """获取器材库存变化趋势"""
        db = get_db()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        sql = """
        SELECT DATE(operate_time) as date, after_quantity
        FROM in_out_record
        WHERE equipment_id = ? AND operate_time >= ? AND operate_time <= ?
        ORDER BY operate_time
        """

        results = db.fetchall(sql, (equipment_id, start_date, end_date))
        return [dict(r) for r in results]
