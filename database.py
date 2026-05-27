# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
数据库连接和初始化模块
"""

import sqlite3
import os
import logging
from datetime import datetime
from contextlib import contextmanager

try:
    import pymysql
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

import config

logger = logging.getLogger(__name__)


class Database:
    """数据库管理类"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.use_sqlite = config.USE_SQLITE
        self.conn = None
        self._connect()

    def _connect(self):
        """建立数据库连接"""
        try:
            if self.use_sqlite:
                db_path = os.path.join(config.BASE_DIR, config.SQLITE_DB_PATH)
                self.conn = sqlite3.connect(db_path, check_same_thread=False)
                self.conn.row_factory = sqlite3.Row
                logger.info(f"SQLite数据库连接成功: {db_path}")
            else:
                if HAS_PYMYSQL:
                    self.conn = pymysql.connect(**config.DB_CONFIG)
                    logger.info("MySQL数据库连接成功")
                else:
                    logger.warning("pymysql未安装，切换到SQLite模式")
                    self.use_sqlite = True
                    db_path = os.path.join(config.BASE_DIR, config.SQLITE_DB_PATH)
                    self.conn = sqlite3.connect(db_path, check_same_thread=False)
                    self.conn.row_factory = sqlite3.Row
                    logger.info(f"SQLite数据库连接成功: {db_path}")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def get_connection(self):
        """获取数据库连接"""
        if self.conn is None:
            self._connect()
        return self.conn

    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器"""
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            cursor.close()

    def execute(self, sql, params=None):
        """执行SQL语句"""
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            self.conn.commit()
            return cursor
        except Exception as e:
            self.conn.rollback()
            logger.error(f"SQL执行失败: {sql}, 错误: {e}")
            raise
        finally:
            cursor.close()

    def executemany(self, sql, params_list):
        """批量执行SQL语句"""
        cursor = self.conn.cursor()
        try:
            cursor.executemany(sql, params_list)
            self.conn.commit()
            return cursor
        except Exception as e:
            self.conn.rollback()
            logger.error(f"SQL批量执行失败: {e}")
            raise
        finally:
            cursor.close()

    def fetchall(self, sql, params=None):
        """查询所有记录"""
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询失败: {e}")
            raise
        finally:
            cursor.close()

    def fetchone(self, sql, params=None):
        """查询单条记录"""
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询失败: {e}")
            raise
        finally:
            cursor.close()

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("数据库连接已关闭")


def init_database():
    """初始化数据库表结构"""
    db = Database()

    # 用户表
    create_user_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        real_name VARCHAR(50),
        role VARCHAR(20) NOT NULL DEFAULT 'operator',
        email VARCHAR(100),
        phone VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        status INTEGER DEFAULT 1
    )
    """

    # 器材信息表
    create_equipment_table = """
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_code VARCHAR(50) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        type VARCHAR(50) NOT NULL,
        specification VARCHAR(200),
        quantity INTEGER DEFAULT 0,
        unit VARCHAR(20) DEFAULT '个',
        purchase_date DATE,
        supplier VARCHAR(200),
        purchase_price DECIMAL(10, 2),
        status INTEGER DEFAULT 1,
        remarks TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )
    """

    # 出入库记录表
    create_in_out_record_table = """
    CREATE TABLE IF NOT EXISTS in_out_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_no VARCHAR(50) UNIQUE NOT NULL,
        equipment_id INTEGER NOT NULL,
        equipment_code VARCHAR(50) NOT NULL,
        equipment_name VARCHAR(100) NOT NULL,
        equipment_type VARCHAR(50) NOT NULL,
        record_type VARCHAR(20) NOT NULL,
        quantity INTEGER NOT NULL,
        before_quantity INTEGER NOT NULL,
        after_quantity INTEGER NOT NULL,
        operator_id INTEGER NOT NULL,
        operator_name VARCHAR(50),
        operate_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        purpose VARCHAR(500),
        remarks TEXT,
        FOREIGN KEY (equipment_id) REFERENCES equipment(id),
        FOREIGN KEY (operator_id) REFERENCES users(id)
    )
    """

    # 操作日志表
    create_log_table = """
    CREATE TABLE IF NOT EXISTS operation_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username VARCHAR(50),
        operation_type VARCHAR(50) NOT NULL,
        operation_module VARCHAR(50),
        operation_desc TEXT,
        ip_address VARCHAR(50),
        operate_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status INTEGER DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """

    # 库存盘点表
    create_check_table = """
    CREATE TABLE IF NOT EXISTS inventory_check (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        check_no VARCHAR(50) UNIQUE NOT NULL,
        equipment_id INTEGER NOT NULL,
        equipment_code VARCHAR(50) NOT NULL,
        equipment_name VARCHAR(100) NOT NULL,
        system_quantity INTEGER NOT NULL,
        actual_quantity INTEGER NOT NULL,
        difference INTEGER NOT NULL,
        check_type VARCHAR(20),
        checker_id INTEGER NOT NULL,
        checker_name VARCHAR(50),
        check_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        remarks TEXT,
        FOREIGN KEY (equipment_id) REFERENCES equipment(id),
        FOREIGN KEY (checker_id) REFERENCES users(id)
    )
    """

    tables = [
        create_user_table,
        create_equipment_table,
        create_in_out_record_table,
        create_log_table,
        create_check_table
    ]

    for sql in tables:
        db.execute(sql)

    # 创建默认管理员账户
    create_default_admin(db)

    logger.info("数据库初始化完成")


def create_default_admin(db):
    """创建默认管理员账户"""
    import hashlib

    # 检查是否已存在管理员
    check_sql = "SELECT id FROM users WHERE username = 'admin'"
    result = db.fetchone(check_sql)

    if not result:
        # 创建默认管理员
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        insert_sql = """
        INSERT INTO users (username, password, real_name, role, email, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute(insert_sql, ('admin', password_hash, '系统管理员', 'admin', 'admin@school.edu.cn', 1))
        logger.info("默认管理员账户已创建: admin / admin123")


def backup_database():
    if config.USE_SQLITE:
        import shutil
        from datetime import datetime

        db_path = os.path.join(config.BASE_DIR, config.SQLITE_DB_PATH)
        backup_dir = config.BACKUP_DIR

        if not os.path.exists(db_path):
            logger.warning("数据库文件不存在，跳过备份")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"sports_equipment_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            shutil.copy2(db_path, backup_path)
            logger.info(f"数据库备份成功: {backup_path}")
            cleanup_old_backups()
            return backup_path
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return None
    else:
        logger.warning("MySQL备份需要使用mysqldump工具")
        return None


def restore_database(backup_path):
    if config.USE_SQLITE:
        import shutil

        db_path = os.path.join(config.BASE_DIR, config.SQLITE_DB_PATH)

        if not os.path.exists(backup_path):
            logger.error(f"备份文件不存在: {backup_path}")
            return False, "备份文件不存在"

        try:
            shutil.copy2(backup_path, db_path)
            logger.info(f"数据库恢复成功: {backup_path}")
            return True, "恢复成功"
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")
            return False, f"恢复失败: {str(e)}"
    else:
        logger.warning("MySQL恢复需要使用mysql命令")
        return False, "MySQL恢复需要使用mysql命令"


def get_backup_files():
    backup_dir = config.BACKUP_DIR
    backup_files = []
    
    if not os.path.exists(backup_dir):
        return []

    for f in os.listdir(backup_dir):
        if f.endswith('.db') and f.startswith('sports_equipment_backup_'):
            full_path = os.path.join(backup_dir, f)
            create_time = os.path.getctime(full_path)
            create_datetime = datetime.fromtimestamp(create_time)
            backup_files.append({
                'filename': f,
                'path': full_path,
                'size': os.path.getsize(full_path),
                'create_time': create_datetime
            })

    backup_files.sort(key=lambda x: x['create_time'], reverse=True)
    return backup_files


def cleanup_old_backups():
    backup_dir = config.BACKUP_DIR
    max_count = config.BACKUP_CONFIG['max_backup_count']

    if not os.path.exists(backup_dir):
        return

    backup_files = []
    for f in os.listdir(backup_dir):
        if f.endswith('.db') or f.endswith('.sql'):
            full_path = os.path.join(backup_dir, f)
            backup_files.append((full_path, os.path.getctime(full_path)))

    backup_files.sort(key=lambda x: x[1], reverse=True)

    for file_path, _ in backup_files[max_count:]:
        try:
            os.remove(file_path)
            logger.info(f"旧备份已清理: {file_path}")
        except Exception as e:
            logger.error(f"清理备份文件失败: {e}")


# 全局数据库实例
_db_instance = None


def get_db():
    """获取数据库实例"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_database()
    print("数据库初始化完成！")
