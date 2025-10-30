#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT认证工具模块

功能说明：
- 提供JWT Token创建和验证功能
- 实现管理员权限控制装饰器
- 支持用户身份验证和权限检查
- 支持Token过期时间控制
- 为多用户协作提供认证支持
"""

from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from lib.response import response

def create_token(identity):
    """
    创建JWT访问令牌
    
    功能：
    - 为用户创建JWT访问令牌
    - 用于API认证和权限验证
    - 支持多用户关联功能
    
    Args:
        identity (int): 用户ID，作为JWT的identity
        
    Returns:
        str: JWT访问令牌字符串
        
    使用示例：
        token = create_token(user.id)
    """
    return create_access_token(identity=str(identity))

def admin_required(f):
    """
    管理员权限装饰器
    
    功能：
    - 验证用户是否已登录
    - 检查用户是否具有管理员权限
    - 保护需要管理员权限的API接口
    
    Args:
        f (function): 需要管理员权限的函数
        
    Returns:
        function: 装饰后的函数
        
    使用示例：
        @admin_required
        def admin_only_function():
            pass
            
    注意：
    - 被装饰的函数需要JWT Token认证
    - 只有role为'admin'的用户才能访问
    - 普通用户访问会返回403错误
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # 导入用户模型
        from model.models import User
        
        # 获取当前用户ID
        current_user_id = get_jwt_identity()
        
        # 查询用户信息
        user = User.get_by_id(int(current_user_id))
        
        # 检查用户是否存在且具有管理员权限
        if not user or user.role != 'admin':
            return response(message="需要管理员权限", code=403)
        
        # 执行原函数
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """
    获取当前登录用户信息
    
    功能：
    - 从JWT Token中获取用户ID
    - 查询并返回当前用户对象
    - 用于获取用户详细信息
    
    Returns:
        User: 当前用户对象，如果未登录返回None
        
    使用示例：
        user = get_current_user()
        if user:
            print(f"当前用户: {user.username}")
            
    注意：
    - 此函数需要在JWT认证的上下文中调用
    - 如果Token无效或用户不存在，返回None
    """
    from model.models import User
    current_user_id = get_jwt_identity()
    return User.get_by_id(int(current_user_id))
