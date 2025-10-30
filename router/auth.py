#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证API模块 - 用户登录认证

功能说明：
- 提供用户登录认证功能
- 支持JWT Token生成和验证
- 支持角色权限控制（管理员/普通用户）
- 保护系统管理功能
"""

from flask import request
from flask_restful import Resource
from werkzeug.security import check_password_hash
from lib.response import response
from model.models import User
from model.models import db
import logging

# 配置日志记录
logger = logging.getLogger(__name__)

class Auth(Resource):
    """
    认证相关API类
    
    功能：
    - 处理用户登录请求
    - 验证用户身份和密码
    - 生成JWT访问令牌
    - 支持多用户关联功能认证
    """
    
    def post(self):
        """
        用户登录接口
        
        功能：
        - 验证用户名和密码
        - 生成JWT访问令牌
        - 返回用户信息和令牌
        
        请求参数：
            {
                "username": "admin",      # 用户名
                "password": "admin123"    # 密码
            }
            
        响应格式：
            {
                "code": 0,
                "msg": "登录成功",
                "data": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "role": "admin",
                    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                }
            }
            
        错误码：
            - 400: 用户名或密码为空
            - 401: 用户名或密码错误
            - 500: 服务器内部错误
        """
        try:
            # 获取请求数据
            data = request.json
            username = data.get('username')
            password = data.get('password')
            
            # 验证必需参数
            if not username or not password:
                return response(message="用户名和密码不能为空", code=400)
            
            # 查找用户
            user = User.get_by_username(username)
            if not user:
                return response(message="用户不存在", code=401)
            
            # 验证密码
            if not check_password_hash(user.password, password):
                return response(message="密码错误", code=401)
            
            # 只允许admin用户登录
            if user.role != 'admin':
                return response(message="只有管理员可以登录系统", code=403)
            
            # 生成JWT Token
            from lib.jwt_utils import create_token
            token = create_token(identity=user.id)
            
            # 构建用户数据
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "token": token
            }
            
            # 记录登录成功
            logger.info(f"用户 {username} 登录成功")
            
            # 返回成功响应
            return response(data=user_data, message="登录成功")
            
        except Exception as e:
            # 记录错误日志
            logger.error(f"登录失败: {e}")
            return response(message="登录失败", code=500)
