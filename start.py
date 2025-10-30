#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
企业级监控系统一键启动脚本

功能说明：
- 检查环境配置和依赖
- 初始化数据库和表结构
- 启动Flask后端服务
- 支持一键部署

使用方法：
python start.py
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """检查依赖是否安装"""
    print("🔍 检查依赖...")
    
    try:
        import flask
        import flask_sqlalchemy
        import flask_migrate
        import flask_jwt_extended
        import pymysql
        import psutil
        print("✅ Python依赖检查通过")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True

def check_database():
    """检查数据库连接"""
    print("🔍 检查数据库连接...")
    
    try:
        from manager import app
        from model.models import db
        
        with app.app_context():
            # 尝试连接数据库
            db.engine.execute('SELECT 1')
            print("✅ 数据库连接正常")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print("请检查数据库配置和连接")
        return False

def init_database():
    """初始化数据库"""
    print("🔧 初始化数据库...")
    
    try:
        result = subprocess.run([sys.executable, 'init_db.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 数据库初始化成功")
            return True
        else:
            print(f"❌ 数据库初始化失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 数据库初始化异常: {e}")
        return False

def start_server():
    """启动服务器"""
    print("🚀 启动服务器...")
    
    try:
        from manager import app
        print("=" * 50)
        print("🎉 系统监控平台启动成功！")
        print("=" * 50)
        print(f"📱 前端地址: http://localhost:5173")
        print(f"🔧 后端地址: http://localhost:8000")
        print(f"📋 管理界面: http://localhost:8000/home")
        print("=" * 50)
        print("按 Ctrl+C 停止服务")
        print("=" * 50)
        
        app.run(debug=True, host='0.0.0.0', port=8000)
    except KeyboardInterrupt:
        print("\n⚠️ 服务已停止")
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")

def main():
    """主函数"""
    print("🚀 系统监控平台启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        sys.exit(1)
    
    # 检查数据库
    if not check_database():
        print("🔧 尝试初始化数据库...")
        if not init_database():
            sys.exit(1)
    
    # 启动服务
    start_server()

if __name__ == "__main__":
    main()
