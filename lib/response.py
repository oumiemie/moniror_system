#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一API响应格式工具模块

功能说明：
- 提供统一的API响应格式
- 标准化错误码和消息
- 支持多用户关联功能的响应
- 确保前后端数据交互一致性

作者: 系统监控平台开发团队
版本: 2.0.0
更新时间: 2025-01-20
"""

def response(data=None, message="success!", code=0):
    """
    统一API响应格式函数
    
    功能：
    - 标准化所有API接口的响应格式
    - 提供统一的错误码和消息结构
    - 支持成功和失败两种响应类型
    
    Args:
        data (any, optional): 响应数据，默认为None
        message (str, optional): 响应消息，默认为"success!"
        code (int, optional): 响应状态码，默认为0（成功）
        
    Returns:
        dict: 标准化的API响应格式
        
    响应格式：
        {
            "code": 0,           # 状态码：0成功，非0失败
            "msg": "success!",   # 响应消息
            "data": []           # 响应数据
        }
        
    状态码说明：
        - 0: 成功
        - 400: 请求参数错误
        - 401: 未授权/认证失败
        - 403: 权限不足
        - 404: 资源不存在
        - 500: 服务器内部错误
        
    使用示例：
        # 成功响应
        return response(data={"id": 1, "name": "test"})
        
        # 错误响应
        return response(message="用户不存在", code=404)
        
        # 空数据响应
        return response(message="操作成功")
    """
    # 如果数据为None，设置为空列表
    if data is None:
        data = []
    
    # 返回标准化的响应格式
    return {
        "code": code,        # 状态码
        "msg": message,      # 响应消息
        "data": data         # 响应数据
    }