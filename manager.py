#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业级系统监控平台 - Flask应用主入口

功能说明：
- 创建和配置Flask应用实例
- 初始化数据库连接和迁移
- 配置JWT认证和CORS支持
- 注册API路由蓝图
- 支持多用户协作和权限控制
- 支持IP地址匹配和批量数据存储
"""

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config.settings import DEBUG, HOST, PORT, JWT_SECRET_KEY

def create_app():
    """
    创建Flask应用实例
    
    功能：
    1. 创建Flask应用并加载配置
    2. 初始化数据库连接和ORM
    3. 配置数据库迁移功能
    4. 设置JWT认证
    5. 注册API路由蓝图
    
    Returns:
        Flask: 配置完成的Flask应用实例
    """
    # 创建Flask应用实例
    app = Flask(__name__)
    
    # 从配置文件加载应用配置
    app.config.from_object('config.settings')

    # ==================== 数据库初始化 ====================
    # 导入数据库连接对象
    from model.models import db
    
    # 将数据库对象绑定到Flask应用
    db.init_app(app)
    
    # 初始化数据库迁移功能
    # 支持数据库schema版本管理和自动迁移
    migrate = Migrate(app, db)

    # ==================== JWT认证配置 ====================
    # 设置JWT密钥
    app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
    
    # 设置JWT Token过期时间
    # 开发环境：24小时，生产环境：1小时
    from config.settings import EXPIRES
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = EXPIRES
    
    # 初始化JWT管理器
    jwt = JWTManager(app)
    
    # 配置JWT错误处理器，返回统一响应格式
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        from lib.response import response
        return response(message="Token已过期", code=401)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        from lib.response import response
        return response(message="无效的Token", code=401)
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        from lib.response import response
        return response(message="缺少认证Token", code=401)

    # ==================== 路由注册 ====================
    # 导入并注册所有API路由蓝图
    # 包括认证、用户管理、服务器管理、监控数据等模块
    import router
    router.init_app(app)

    return app

# ==================== 应用实例创建 ====================
# 创建Flask应用实例
app = create_app()

# ==================== CORS跨域配置 ====================
# 配置跨域资源共享，允许前端访问后端API
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://192.168.100.1:5173"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-API-Key"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# ==================== 应用启动 ====================
if __name__ == "__main__":
    """
    直接运行此文件时启动Flask开发服务器
    
    注意：
    - 这是开发环境启动方式
    - 生产环境请使用Gunicorn等WSGI服务器
    - 详细部署说明请参考DEPLOYMENT_GUIDE.md
    """
    app.run(debug=DEBUG, host=HOST, port=PORT)


