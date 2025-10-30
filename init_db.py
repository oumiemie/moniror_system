#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本

功能说明：
- 创建数据库表结构
- 创建管理员用户
- 初始化基础数据
- 支持一键启动

使用方法：
python init_db.py
"""

import os
import sys
from werkzeug.security import generate_password_hash

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manager import app
from model.models import db
from model.models import User, Server

def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    with app.app_context():
        try:
            # 创建所有表
            print("📋 创建数据库表...")
            db.create_all()
            print("✅ 数据库表创建成功")
            
            # 检查是否已存在管理员用户
            admin_user = User.get_by_username('admin')
            if admin_user:
                print("⚠️ 管理员用户已存在，跳过创建")
            else:
                # 创建管理员用户
                print("👤 创建管理员用户...")
                admin = User(
                    username='admin',
                    password=generate_password_hash('admin123'),
                    email='admin@example.com',
                    role='admin'
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ 管理员用户创建成功: admin/admin123")
            
            # 创建示例服务器（可选）
            print("🖥️ 检查示例服务器...")
            example_server = Server.get_by_ip('127.0.0.1')
            if not example_server:
                print("📝 创建示例服务器...")
                server = Server(
                    server_name='本地测试服务器',
                    ip_address='127.0.0.1',
                    port=22,
                    status='online'
                )
                db.session.add(server)
                db.session.commit()
                print("✅ 示例服务器创建成功")
            else:
                print("⚠️ 示例服务器已存在，跳过创建")
            
            print("\n🎉 数据库初始化完成！")
            print("=" * 50)
            print("📋 系统信息:")
            print(f"   管理员账号: admin")
            print(f"   管理员密码: admin123")
            print(f"   管理员邮箱: admin@example.com")
            print(f"   数据库地址: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("=" * 50)
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            return False
    
    return True

def main():
    """主函数"""
    print("🔧 系统监控平台 - 数据库初始化工具")
    print("=" * 50)
    
    try:
        success = init_database()
        if success:
            print("\n✅ 初始化成功！现在可以启动服务了。")
            print("启动命令: python manager.py")
        else:
            print("\n❌ 初始化失败！请检查错误信息。")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ 初始化被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 初始化异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
