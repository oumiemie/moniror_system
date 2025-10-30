#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API密钥认证工具模块

功能说明：
- 提供API密钥认证和验证功能
- 保护监控数据提交接口
- 支持多服务器API密钥管理
- 为监控Agent提供安全认证
- 支持API密钥过期时间控制
"""

from functools import wraps
from flask import request
from lib.response import response
from config.settings import DEFAULT_API_KEY, DEBUG
import hashlib
import time

# ==================== API密钥配置 ====================
# API密钥配置（从配置文件读取）
# 支持多服务器使用不同的API密钥
API_KEYS = {
    "default": DEFAULT_API_KEY,        # 默认API密钥
    "server_1": "key_abc123def456",    # 服务器1专用密钥
    "server_2": "key_xyz789uvw012",    # 服务器2专用密钥
    "server_3": "key_mno345pqr678"     # 服务器3专用密钥
}

# API密钥过期时间配置（秒）
# 开发环境：7天，生产环境：30天
API_KEY_EXPIRES = 2592000 if not DEBUG else 604800  # 30天或7天

def api_key_required(f):
    """
    API密钥认证装饰器
    
    功能：
    - 验证请求头中的API密钥
    - 保护需要API密钥的接口
    - 支持监控数据提交认证
    
    Args:
        f (function): 需要API密钥认证的函数
        
    Returns:
        function: 装饰后的函数
        
    使用示例：
        @api_key_required
        def submit_monitor_data():
            pass
            
    注意：
    - 需要在请求头中提供X-API-Key
    - 密钥必须在有效密钥列表中
    - 用于监控Agent数据提交认证
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 从请求头获取API密钥
        api_key = request.headers.get('X-API-Key')
        
        # 检查是否提供了API密钥
        if not api_key:
            return response(message="缺少API密钥", code=401)
        
        # 验证API密钥是否有效
        if api_key not in API_KEYS.values():
            # 调试信息：打印密钥验证失败详情
            print(f"API密钥验证失败:")
            print(f"  提供的密钥: {api_key}")
            print(f"  有效密钥列表: {list(API_KEYS.values())}")
            return response(message="无效的API密钥", code=401)
        
        # 验证通过，执行原函数
        return f(*args, **kwargs)
    return decorated_function

def generate_api_key(server_name):
    """
    生成API密钥
    
    功能：
    - 为指定服务器生成唯一的API密钥
    - 基于服务器名称和时间戳生成
    - 使用SHA256哈希确保安全性
    
    Args:
        server_name (str): 服务器名称
        
    Returns:
        str: 生成的API密钥（16位）
        
    使用示例：
        key = generate_api_key("web_server_01")
        print(f"生成的API密钥: {key}")
    """
    # 获取当前时间戳
    timestamp = str(int(time.time()))
    
    # 组合服务器名称和时间戳
    raw_key = f"{server_name}_{timestamp}"
    
    # 使用SHA256生成哈希值，取前16位
    return hashlib.sha256(raw_key.encode()).hexdigest()[:16]

def validate_api_key(api_key):
    """
    验证API密钥是否有效
    
    功能：
    - 检查API密钥是否在有效密钥列表中
    - 用于手动验证API密钥
    
    Args:
        api_key (str): 要验证的API密钥
        
    Returns:
        bool: True表示有效，False表示无效
        
    使用示例：
        if validate_api_key("key_abc123def456"):
            print("API密钥有效")
        else:
            print("API密钥无效")
    """
    return api_key in API_KEYS.values()
