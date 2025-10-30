#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能告警邮件处理模块

功能说明：
- 基于IP地址匹配的告警系统
- 支持CPU、内存、磁盘使用率告警
- 提供多级别告警（警告、严重、紧急）
- 持续告警检测机制，避免告警风暴
- 支持多用户关联的告警通知

告警流程：
1. 监控Agent提交数据时触发告警检查
2. 根据IP地址查找服务器记录
3. 检查监控数据是否持续超过阈值（5分钟）
4. 向所有关联用户发送告警邮件

核心函数：
- check_and_send_alert_by_ip(): 基于IP地址的告警检查
- check_sustained_alert_by_ip(): 基于IP地址的持续告警检查
"""

from datetime import datetime, timedelta
from config.settings import DEFAULT_THRESHOLDS, ALERT_TEMPLATES, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_SENDER
from model.models import Server, User
import logging

# ==================== 日志配置 ====================
# 配置日志记录
logger = logging.getLogger(__name__)

def check_and_send_alert_by_ip(ip_address, metric_type, value):
    """
    根据IP地址检查阈值并发送告警
    
    流程：
    1. 根据IP地址找到服务器
    2. 获取服务器的所有关联用户
    3. 检查是否持续超过阈值（5分钟）
    4. 向所有关联用户的邮箱发送告警
    """
    try:
        # 1. 获取服务器信息
        server = Server.get_by_ip(ip_address)
        if not server:
            logger.error(f"服务器 {ip_address} 不存在")
            return False
        
        # 2. 获取告警用户列表
        alert_users = server.get_alert_users()
        if not alert_users:
            logger.error(f"服务器 {ip_address} 没有关联用户")
            return False
        
        # 3. 获取告警阈值
        thresholds = DEFAULT_THRESHOLDS[metric_type]
        
        # 4. 检查告警级别
        alert_level = determine_alert_level(value, thresholds)
        
        if alert_level:
            # 5. 检查是否持续超过阈值（5分钟）
            if not check_sustained_alert_by_ip(ip_address, metric_type, value, minutes=5):
                return True
            
            # 6. 向所有关联用户发送告警邮件
            success_count = 0
            total_count = len(alert_users)
            
            for user in alert_users:
                success = send_alert_email(
                    user.email, 
                    server.server_name, 
                    metric_type, 
                    value, 
                    alert_level
                )
                
                if success:
                    success_count += 1
                else:
                    logger.error(f"告警发送失败: {server.server_name} -> {user.email}")
            
            if success_count > 0:
                logger.info(f"告警发送完成: {success_count}/{total_count} 成功")
            return success_count > 0
        else:
            return True
        
    except Exception as e:
        logger.error(f"告警检查失败: {e}")
        return False



def check_sustained_alert_by_ip(ip_address, metric_type, value, minutes=1):
    """
    根据IP地址检查是否持续超过阈值
    
    Args:
        ip_address (str): 服务器IP地址
        metric_type (str): 监控指标类型
        value (float): 当前值
        minutes (int): 持续分钟数，默认5分钟
        
    Returns:
        bool: 是否持续超过阈值
    """
    from model.models import MonitorData
    
    # 获取最近N分钟的数据
    start_time = datetime.utcnow() - timedelta(minutes=minutes)
    
    # 根据IP地址查询最近N分钟的数据
    recent_data = MonitorData.get_by_ip(ip_address, start_time)
    
    if len(recent_data) < 3:  # 至少需要3个数据点
        return False
    
    # 获取阈值
    thresholds = DEFAULT_THRESHOLDS[metric_type]
    alert_level = determine_alert_level(value, thresholds)
    
    if not alert_level:
        return False
    
    # 检查是否所有数据都超过对应阈值
    threshold_value = thresholds[alert_level]
    sustained_count = 0
    
    for data in recent_data:
        if metric_type == 'cpu' and data.cpu_value >= threshold_value:
            sustained_count += 1
        elif metric_type == 'memory' and data.memory_value >= threshold_value:
            sustained_count += 1
        elif metric_type == 'disk' and data.disk_value >= threshold_value:
            sustained_count += 1
    
    # 如果80%以上的数据都超过阈值，认为持续告警
    return sustained_count >= len(recent_data) * 0.8




def determine_alert_level(value, thresholds):
    """确定告警级别"""
    if value >= thresholds['emergency']:
        return 'emergency'
    elif value >= thresholds['critical']:
        return 'critical'
    elif value >= thresholds['warning']:
        return 'warning'
    return None

def send_alert_email(email, server_name, metric_type, value, level):
    """发送告警邮件"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        # 生成告警消息
        template = ALERT_TEMPLATES[level]
        message = template.format(
            server_name=server_name,
            metric_type=metric_type,
            value=value,
            threshold=get_threshold_by_level(level, metric_type)
        )
        
        # 创建邮件
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = SMTP_SENDER
        msg['To'] = email
        msg['Subject'] = f"【{level.upper()}】服务器 {server_name} 监控告警"
        
        # 发送邮件
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_SENDER, email, msg.as_string())
        
        return True
        
    except Exception as e:
        logger.error(f"发送告警邮件失败: {e}")
        return False

def get_threshold_by_level(level, metric_type):
    """根据级别获取阈值"""
    thresholds = DEFAULT_THRESHOLDS[metric_type]
    if level == 'emergency':
        return thresholds['emergency']
    elif level == 'critical':
        return thresholds['critical']
    elif level == 'warning':
        return thresholds['warning']
    return 0

