#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由注册模块

功能说明：
- 统一管理所有API路由注册
- 支持多用户关联功能的API接口
- 提供RESTful API设计
- 集成认证、用户管理、服务器管理、监控数据等功能

作者: 系统监控平台开发团队
版本: 2.0.0
更新时间: 2025-01-20
"""

from flask import Blueprint
from flask_restful import Api

# ==================== 蓝图和API实例创建 ====================
# 创建监控系统蓝图，URL前缀为/api
mon_bp = Blueprint("monitor", __name__, url_prefix="/api")

# 创建Flask-RESTful API实例
api = Api(mon_bp)

# ==================== 路由模块导入 ====================
# 导入所有路由模块
from . import auth      # 认证模块
from . import user      # 用户管理模块
from . import server    # 服务器管理模块
from . import monitor   # 监控数据模块

def init_app(app):
    """
    初始化应用并注册所有路由
    
    功能：
    - 注册监控系统蓝图到Flask应用
    - 注册所有API资源路由
    - 支持多用户关联功能的API接口
    - 提供统一的API访问入口
    
    Args:
        app (Flask): Flask应用实例
        
    API路由说明：
    - 认证路由: /api/auth/login
    - 用户管理: /api/users, /api/profile
    - 服务器管理: /api/servers, /api/user-servers
    - 多用户关联: /api/servers/{id}/users
    - 监控数据: /api/monitor/data, /api/monitor/stats
    """
    # 注册蓝图到Flask应用
    app.register_blueprint(mon_bp)
    
    # ==================== API资源导入 ====================
    # 导入所有API资源类
    from .auth import Auth
    from .user import UserManagement, UserProfile, UserResetPassword
    from .server import ServerManagement, UserServers, ServerUserAPI
    from .monitor import MonitorDataAPI, MonitorStats
    
    # ==================== 认证路由 ====================
    # 用户登录认证（无需认证）
    api.add_resource(Auth, '/auth/login')
    
    # ==================== 用户管理路由 ====================
    # 用户CRUD操作（仅管理员）
    api.add_resource(UserManagement, '/users', '/users/<int:user_id>')
    # 用户个人信息（需要认证）
    api.add_resource(UserProfile, '/profile')
    # 用户密码重置（仅管理员）
    api.add_resource(UserResetPassword, '/users/reset-password')
    
    # ==================== 服务器管理路由 ====================
    # 服务器CRUD操作（仅管理员）
    api.add_resource(ServerManagement, '/servers', '/servers/<int:server_id>')
    # 用户关联的服务器列表（需要认证）
    api.add_resource(UserServers, '/user-servers')
    # 服务器多用户关联管理（仅管理员）
    api.add_resource(ServerUserAPI, '/servers/<int:server_id>/users', '/servers/<int:server_id>/users/<int:user_id>')
    
    # ==================== 监控数据路由 ====================
    # 监控数据提交（API密钥认证）和查询（管理员认证）
    api.add_resource(MonitorDataAPI, '/monitor/data')
    # 监控数据统计（需要认证）
    api.add_resource(MonitorStats, '/monitor/stats')
    
    # ==================== 其他路由 ====================
    # 首页路由（无需认证）
    @app.route("/home")
    def index():
        """
        系统首页
        
        功能：
        - 提供系统基本信息
        - 引导用户使用前端界面
        
        Returns:
            str: 系统欢迎信息
        """
        return "系统监控平台 - 请使用前端界面访问"


