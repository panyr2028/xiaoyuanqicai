# -*- coding: utf-8 -*-
"""
校园体育器材出入库管理系统
用户认证和权限管理模块
"""

import hashlib
from datetime import datetime

from database import get_db
from logger import log_operation, log_info, log_error


class UserAuth:
    """用户认证类"""

    @staticmethod
    def hash_password(password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, password_hash):
        """验证密码"""
        return UserAuth.hash_password(password) == password_hash

    @staticmethod
    def login(username, password):
        """用户登录"""
        db = get_db()
        sql = "SELECT * FROM users WHERE username = ? AND status = 1"
        user = db.fetchone(sql, (username,))

        if not user:
            return None, "用户名不存在或账户已禁用"

        if not UserAuth.verify_password(password, user['password']):
            log_error(f"用户 {username} 登录失败：密码错误")
            return None, "密码错误"

        # 更新最后登录时间
        update_sql = "UPDATE users SET last_login = ? WHERE id = ?"
        db.execute(update_sql, (datetime.now(), user['id']))

        log_info(f"用户 {username} 登录成功")

        # 记录登录日志
        log_operation(user['id'], username, 'login', 'auth', f'用户 {username} 登录系统')

        return dict(user), "登录成功"

    @staticmethod
    def logout(user_id, username):
        """用户登出"""
        log_operation(user_id, username, 'logout', 'auth', f'用户 {username} 退出系统')
        return True, "登出成功"

    @staticmethod
    def register(username, password, real_name, role='operator', email='', phone=''):
        """用户注册"""
        db = get_db()

        # 检查用户名是否已存在
        check_sql = "SELECT id FROM users WHERE username = ?"
        if db.fetchone(check_sql, (username,)):
            return False, "用户名已存在"

        # 创建新用户
        password_hash = UserAuth.hash_password(password)
        insert_sql = """
        INSERT INTO users (username, password, real_name, role, email, phone)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        try:
            db.execute(insert_sql, (username, password_hash, real_name, role, email, phone))
            log_info(f"新用户注册成功: {username}")
            return True, "注册成功"
        except Exception as e:
            log_error(f"用户注册失败: {e}")
            return False, f"注册失败: {str(e)}"

    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码"""
        db = get_db()

        # 验证旧密码
        sql = "SELECT password FROM users WHERE id = ?"
        user = db.fetchone(sql, (user_id,))
        if not user:
            return False, "用户不存在"

        if not UserAuth.verify_password(old_password, user['password']):
            log_error(f"用户ID {user_id} 修改密码失败：旧密码错误")
            return False, "旧密码错误"

        # 更新新密码
        new_password_hash = UserAuth.hash_password(new_password)
        update_sql = "UPDATE users SET password = ?, updated_at = ? WHERE id = ?"
        db.execute(update_sql, (new_password_hash, datetime.now(), user_id))

        log_info(f"用户ID {user_id} 密码修改成功")
        log_operation(user_id, '', 'change_password', 'auth', '修改密码')

        return True, "密码修改成功"

    @staticmethod
    def reset_password(user_id, new_password, admin_id=None):
        """管理员重置用户密码"""
        db = get_db()

        new_password_hash = UserAuth.hash_password(new_password)
        update_sql = "UPDATE users SET password = ?, updated_at = ? WHERE id = ?"
        db.execute(update_sql, (new_password_hash, datetime.now(), user_id))

        log_info(f"管理员 {admin_id} 重置了用户ID {user_id} 的密码")
        if admin_id:
            log_operation(admin_id, '', 'reset_password', 'auth', f'重置用户ID {user_id} 的密码')

        return True, "密码重置成功"


class Permission:
    """权限管理类"""

    PERMISSIONS = {
        'admin': ['all'],
        'operator': [
            'equipment_view', 'equipment_add', 'equipment_edit', 'equipment_delete',
            'inventory_view', 'in_out_record', 'report_view', 'report_export'
        ]
    }

    @staticmethod
    def check_permission(role, permission):
        """检查权限"""
        if role not in Permission.PERMISSIONS:
            return False
        perms = Permission.PERMISSIONS[role]
        return 'all' in perms or permission in perms

    @staticmethod
    def get_permissions(role):
        """获取用户角色权限列表"""
        return Permission.PERMISSIONS.get(role, [])


class UserManager:
    """用户管理类"""

    @staticmethod
    def get_user_by_id(user_id):
        db = get_db()
        sql = "SELECT * FROM users WHERE id = ?"
        user = db.fetchone(sql, (user_id,))
        return dict(user) if user else None

    @staticmethod
    def get_by_id(user_id):
        return UserManager.get_user_by_id(user_id)

    @staticmethod
    def get_user_by_username(username):
        db = get_db()
        sql = "SELECT * FROM users WHERE username = ?"
        user = db.fetchone(sql, (username,))
        return dict(user) if user else None

    @staticmethod
    def get_all_users(page=1, page_size=20, role=None, keyword=''):
        db = get_db()
        offset = (page - 1) * page_size

        sql = "SELECT * FROM users WHERE 1=1"
        count_sql = "SELECT COUNT(*) as total FROM users WHERE 1=1"
        params = []
        count_params = []

        if role:
            sql += " AND role = ?"
            count_sql += " AND role = ?"
            params.append(role)
            count_params.append(role)

        if keyword:
            sql += " AND (username LIKE ? OR real_name LIKE ? OR email LIKE ?)"
            count_sql += " AND (username LIKE ? OR real_name LIKE ? OR email LIKE ?)"
            keyword_pattern = f"%{keyword}%"
            params.extend([keyword_pattern, keyword_pattern, keyword_pattern])
            count_params.extend([keyword_pattern, keyword_pattern, keyword_pattern])

        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        users = db.fetchall(sql, params)
        total_result = db.fetchone(count_sql, count_params)
        total = total_result['total'] if total_result else 0

        return [dict(user) for user in users], total

    @staticmethod
    def get_all(page=1, page_size=20, role=None, keyword=''):
        return UserManager.get_all_users(page, page_size, role, keyword)

    @staticmethod
    def update_user(user_id, real_name=None, email=None, phone=None, role=None, status=None):
        """更新用户信息"""
        db = get_db()

        updates = []
        params = []

        if real_name is not None:
            updates.append("real_name = ?")
            params.append(real_name)
        if email is not None:
            updates.append("email = ?")
            params.append(email)
        if phone is not None:
            updates.append("phone = ?")
            params.append(phone)
        if role is not None:
            updates.append("role = ?")
            params.append(role)
        if status is not None:
            updates.append("status = ?")
            params.append(status)

        if not updates:
            return False, "没有需要更新的字段"

        updates.append("updated_at = ?")
        params.append(datetime.now())
        params.append(user_id)

        sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"

        try:
            db.execute(sql, params)
            log_info(f"用户ID {user_id} 信息已更新")
            return True, "更新成功"
        except Exception as e:
            log_error(f"更新用户信息失败: {e}")
            return False, f"更新失败: {str(e)}"

    @staticmethod
    def delete_user(user_id, current_user_id=None):
        """删除用户"""
        db = get_db()

        # 不能删除自己
        if current_user_id and current_user_id == user_id:
            return False, "不能删除当前登录用户"

        # 不能删除管理员
        user = UserManager.get_user_by_id(user_id)
        if user and user['role'] == 'admin':
            return False, "不能删除管理员账户"

        sql = "DELETE FROM users WHERE id = ?"
        try:
            db.execute(sql, (user_id,))
            log_info(f"用户ID {user_id} 已删除")
            return True, "删除成功"
        except Exception as e:
            log_error(f"删除用户失败: {e}")
            return False, f"删除失败: {str(e)}"
