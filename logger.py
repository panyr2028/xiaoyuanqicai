# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
日志管理模块
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

import config


class Logger:
    """日志管理类"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name='SportsEquipment'):
        """获取日志记录器"""
        if name in cls._loggers:
            return cls._loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.LOG_CONFIG['level']))

        if logger.handlers:
            return logger

        log_dir = os.path.join(config.BASE_DIR, config.LOG_CONFIG['log_file']).rsplit('/', 1)[0]
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        log_file = os.path.join(config.BASE_DIR, config.LOG_CONFIG['log_file'])
        handler = RotatingFileHandler(
            log_file,
            maxBytes=config.LOG_CONFIG['max_bytes'],
            backupCount=config.LOG_CONFIG['backup_count'],
            encoding='utf-8'
        )

        formatter = logging.Formatter(config.LOG_CONFIG['format'])
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        cls._loggers[name] = logger
        return logger


def log_operation(user_id, username, operation_type, operation_module, operation_desc, ip_address=None):
    """记录操作日志到数据库"""
    from database import get_db

    db = get_db()
    try:
        sql = """
        INSERT INTO operation_log (user_id, username, operation_type, operation_module, operation_desc, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        db.execute(sql, (user_id, username, operation_type, operation_module, operation_desc, ip_address))
    except Exception as e:
        logger = Logger.get_logger()
        logger.error(f"记录操作日志失败: {e}")


def get_operation_logs(user_id=None, operation_type=None, start_time=None, end_time=None, limit=100):
    """查询操作日志"""
    from database import get_db

    db = get_db()
    sql = "SELECT * FROM operation_log WHERE 1=1"
    params = []

    if user_id:
        sql += " AND user_id = ?"
        params.append(user_id)
    if operation_type:
        sql += " AND operation_type = ?"
        params.append(operation_type)
    if start_time:
        sql += " AND operate_time >= ?"
        params.append(start_time)
    if end_time:
        sql += " AND operate_time <= ?"
        params.append(end_time)

    sql += " ORDER BY operate_time DESC LIMIT ?"
    params.append(limit)

    return db.fetchall(sql, params)


def log_info(message, module='System'):
    """记录信息日志"""
    logger = Logger.get_logger(module)
    logger.info(message)


def log_error(message, module='System'):
    """记录错误日志"""
    logger = Logger.get_logger(module)
    logger.error(message)


def log_warning(message, module='System'):
    """记录警告日志"""
    logger = Logger.get_logger(module)
    logger.warning(message)


def log_debug(message, module='System'):
    """记录调试日志"""
    logger = Logger.get_logger(module)
    logger.debug(message)
