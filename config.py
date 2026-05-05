# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
配置文件
"""

import os

# 应用基本配置
APP_NAME = "校园体育器材出入库管理系统"
APP_VERSION = "1.0.0"
APP_AUTHOR = "校园体育器材管理部"

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'sports_equipment_db',
    'charset': 'utf8mb4'
}

# SQLite备用配置（用于便携部署）
USE_SQLITE = True
SQLITE_DB_PATH = 'sports_equipment.db'

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': 'logs/system.log',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# 备份配置
BACKUP_CONFIG = {
    'backup_dir': 'backups',
    'auto_backup': True,
    'backup_interval': 24,  # 小时
    'max_backup_count': 10
}

# 库存预警配置
INVENTORY_WARNING_CONFIG = {
    'basketball': 10,      # 篮球最低库存
    'volleyball': 10,     # 排球最低库存
    'badminton_racket': 20,  # 羽毛球拍最低库存
    'pingpong_racket': 20,   # 乒乓球拍最低库存
    'tennis_racket': 10     # 网球拍最低库存
}

# 器材类型配置
EQUIPMENT_TYPES = [
    ('basketball', '篮球'),
    ('volleyball', '排球'),
    ('badminton_racket', '羽毛球拍'),
    ('pingpong_racket', '乒乓球拍'),
    ('tennis_racket', '网球拍'),
    ('football', '足球')
]

# 用户角色配置
USER_ROLES = {
    'admin': {
        'name': '系统管理员',
        'permissions': ['all']
    },
    'operator': {
        'name': '普通操作员',
        'permissions': ['equipment_view', 'equipment_add', 'equipment_edit',
                        'inventory_view', 'in_out_record', 'report_view']
    }
}

# 分页配置
PAGE_CONFIG = {
    'default_page_size': 20,
    'page_size_options': [10, 20, 50, 100]
}

# 导出配置
EXPORT_CONFIG = {
    'excel_encoding': 'utf-8-sig',
    'csv_encoding': 'utf-8-sig',
    'export_dir': 'exports'
}

# 系统路径配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')

# 确保必要目录存在
for directory in [DATA_DIR, LOG_DIR, BACKUP_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)
