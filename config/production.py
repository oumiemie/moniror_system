"""
生产环境配置
"""

import os

class ProductionConfig:
    """生产环境配置类"""
    
    # 基础配置
    DEBUG = False
    TESTING = False
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///monitor_production.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-super-secret-jwt-key-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时
    
    # API密钥配置
    API_KEY = os.environ.get('API_KEY') or 'production-api-key-change-me'
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # 告警阈值配置
    DEFAULT_THRESHOLDS = {
        'cpu': {
            'warning': 70.0,
            'critical': 85.0,
            'emergency': 95.0
        },
        'memory': {
            'warning': 75.0,
            'critical': 85.0,
            'emergency': 95.0
        },
        'disk': {
            'warning': 80.0,
            'critical': 90.0,
            'emergency': 95.0
        }
    }
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or '/app/logs/monitor.log'
    
    # 监控配置
    MONITOR_INTERVAL = int(os.environ.get('MONITOR_INTERVAL') or 30)
    DATA_RETENTION_DAYS = int(os.environ.get('DATA_RETENTION_DAYS') or 30)
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-super-secret-key-change-in-production'
    WTF_CSRF_ENABLED = True
    
    # 性能配置
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
