"""
用户管理API接口
支持角色权限控制和密码管理
"""

from flask import request
from flask_restful import Resource
from werkzeug.security import generate_password_hash
from lib.response import response
from model.models import db
from model.models import User
from lib.jwt_utils import admin_required, get_current_user
import logging

logger = logging.getLogger(__name__)

class UserManagement(Resource):
    """用户管理API"""
    
    @admin_required
    def get(self, user_id=None):
        """获取用户列表或指定用户信息"""
        try:
            if user_id:
                # 获取指定用户信息
                user = User.get_by_id(user_id)
                if not user:
                    return response(message="用户不存在", code=404)
                
                user_data = dict(user)
                return response(data=user_data, message="获取用户信息成功")
            else:
                # 获取所有用户列表
                users = User.get_all()
                user_list = [dict(user) for user in users]
                return response(data=user_list, message="获取用户列表成功")
                
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return response(message="获取用户信息失败", code=500)
    
    @admin_required
    def post(self):
        """添加用户（仅管理员）"""
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            # 强制设置角色为user，不允许创建admin
            role = 'user'
            
            # 验证必需字段
            if not all([username, password, email]):
                return response(message="用户名、密码和邮箱不能为空", code=400)
            
            # 检查用户名是否已存在
            if User.get_by_username(username):
                return response(message="用户名已存在", code=400)
            
            # 创建用户
            hashed_password = generate_password_hash(password)
            user = User.create(username, hashed_password, email, role)
            
            user_data = dict(user)
            logger.info(f"管理员创建用户: {username}")
            return response(data=user_data, message="用户创建成功")
            
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return response(message="创建用户失败", code=500)
    
    @admin_required
    def put(self, user_id):
        """更新用户信息（仅管理员）"""
        try:
            data = request.json
            user = User.get_by_id(user_id)
            if not user:
                return response(message="用户不存在", code=404)
            
            # 更新用户信息
            if 'username' in data:
                # 检查新用户名是否已存在
                existing_user = User.get_by_username(data['username'])
                if existing_user and existing_user.id != user_id:
                    return response(message="用户名已存在", code=400)
                user.username = data['username']
            
            if 'email' in data:
                user.email = data['email']
            
            # 禁止修改用户角色，保持原有角色
            # if 'role' in data:
            #     user.role = data['role']
            
            if 'password' in data and data['password']:
                user.password = generate_password_hash(data['password'])
            
            db.session.commit()
            
            user_data = dict(user)
            logger.info(f"管理员更新用户: {user.username}")
            return response(data=user_data, message="用户更新成功")
            
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return response(message="更新用户失败", code=500)
    
    @admin_required
    def delete(self, user_id):
        """删除用户（仅管理员）"""
        try:
            user = User.get_by_id(user_id)
            if not user:
                return response(message="用户不存在", code=404)
            
            # 检查是否为管理员
            if user.role == 'admin':
                return response(message="不能删除管理员用户", code=400)
            
            username = user.username
            User.delete(user_id)
            
            logger.info(f"管理员删除用户: {username}")
            return response(message="用户删除成功")
            
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return response(message="删除用户失败", code=500)

class UserProfile(Resource):
    """用户个人信息API（仅管理员）"""
    
    @admin_required
    def get(self):
        """获取当前用户信息（仅管理员）"""
        try:
            user = get_current_user()
            if not user:
                return response(message="用户未登录", code=401)
            
            user_data = dict(user)
            return response(data=user_data, message="获取用户信息成功")
            
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return response(message="获取用户信息失败", code=500)

class UserResetPassword(Resource):
    """用户密码重置API（仅管理员）"""
    
    @admin_required
    def put(self):
        """重置用户密码（仅管理员）"""
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password')
            
            # 验证必需字段
            if not all([username, password]):
                return response(message="用户名和新密码不能为空", code=400)
            
            # 查找用户
            user = User.get_by_username(username)
            if not user:
                return response(message="用户不存在", code=404)
            
            # 更新密码
            user.password = generate_password_hash(password)
            db.session.commit()
            
            logger.info(f"管理员重置用户密码: {username}")
            return response(message="密码重置成功")
            
        except Exception as e:
            logger.error(f"重置密码失败: {e}")
            return response(message="重置密码失败", code=500)
