"""
企业级监控系统配置文件
包含数据库连接、JWT配置、邮件配置、告警阈值等核心配置
支持环境变量配置，便于不同环境部署
"""

import os
import secrets

# ==================== 应用基础配置 ====================
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'  # 调试模式，生产环境应设为False
HOST = os.getenv('HOST', '0.0.0.0')  # 监听地址，0.0.0.0表示监听所有网络接口
PORT = int(os.getenv('PORT', '8000'))  # 监听端口

# ==================== 数据库配置 ====================
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')  # MySQL服务器地址
DB_USER = os.getenv('DB_USER', 'root')  # MySQL用户名
DB_PASS = os.getenv('DB_PASS', 'LCW200368')  # MySQL密码
DB_PORT = int(os.getenv('DB_PORT', '3306'))  # MySQL端口
DATABASE = os.getenv('DATABASE', 'monitor_db')  # 数据库名称

# ORM 数据库连接设置，底层使用pymysql驱动
# 格式：数据库类型+驱动://用户名:密码@数据库地址:端口/数据库名称?额外参数
SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DATABASE}?charset=utf8'

# JWT Token过期时间（秒）
# 开发环境：24小时，生产环境：1小时
EXPIRES = 3600 if not DEBUG else 86400

# ==================== 安全密钥配置 ====================
# 密钥配置 - 开发环境使用固定值，生产环境使用环境变量
if DEBUG:
    # 开发环境：使用固定密钥，便于调试
    SECRET_KEY = 'dev-secret-key-123456'  # Flask应用密钥
    JWT_SECRET_KEY = 'dev-jwt-secret-key-123456'  # JWT签名密钥
else:
    # 生产环境：使用环境变量或自动生成
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_urlsafe(32))
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_urlsafe(32))

# ==================== 邮件配置 ====================
# SMTP邮件服务器配置，用于发送告警邮件
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.qq.com')           # QQ邮箱SMTP服务器
SMTP_PORT = int(os.getenv('SMTP_PORT', '465'))                     # QQ邮箱SMTP端口
SMTP_USER = os.getenv('SMTP_USER', '3075901913@qq.com')     # 你的QQ邮箱地址
SMTP_PASS = os.getenv('SMTP_PASS', 'aukgzqmlvbgedgee')        # 你的QQ邮箱授权码（16位）
SMTP_SENDER = os.getenv('SMTP_SENDER', '3075901913@qq.com')   # 发件人邮箱（通常与SMTP_USER相同）

# ==================== 告警阈值配置 ====================
# 默认告警阈值配置，支持CPU、内存、磁盘三种指标
DEFAULT_THRESHOLDS = {
    'cpu': {'warning': 70, 'critical': 85, 'emergency': 95},  # CPU使用率阈值
    'memory': {'warning': 75, 'critical': 90, 'emergency': 95},  # 内存使用率阈值
    'disk': {'warning': 80, 'critical': 90, 'emergency': 95}  # 磁盘使用率阈值
}

# ==================== 告警模板配置 ====================
# 告警邮件内容模板，支持变量替换
ALERT_TEMPLATES = {
    'warning': "【警告】服务器 {server_name} 的 {metric_type} 使用率为 {value}%，超过警告阈值 {threshold}%",
    'critical': "【严重】服务器 {server_name} 的 {metric_type} 使用率为 {value}%，超过严重阈值 {threshold}%",
    'emergency': "【紧急】服务器 {server_name} 的 {metric_type} 使用率为 {value}%，超过紧急阈值 {threshold}%"
}

# ==================== API密钥配置 ====================
# API密钥配置 - 开发环境固定，生产环境自动生成
if DEBUG:
    DEFAULT_API_KEY = 'dev-api-key-123456'  # 开发环境固定API密钥
else:
    DEFAULT_API_KEY = os.getenv('DEFAULT_API_KEY', f'key_{secrets.token_urlsafe(16)}')