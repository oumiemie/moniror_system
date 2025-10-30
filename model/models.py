"""
企业级监控系统数据模型
包含用户、服务器、监控数据三个核心表和关联表

数据库设计说明：
- users: 用户表，存储管理员和普通用户信息，支持角色权限控制
- servers: 服务器表，存储被监控的服务器信息，支持IP地址匹配
- server_users: 服务器-用户关联表，支持多对多关系，实现多用户协作
- monitor_data: 监控数据表，批量存储CPU、内存、磁盘使用率数据

关联关系：
User(N) <-> Server(N) (多对多，通过server_users表)
Server(1) -> MonitorData(N) (一对多)
一个服务器可以关联多个用户，一个用户也可以关联多个服务器
一个服务器可以有多个监控数据记录，支持批量数据存储
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 创建数据库实例
db = SQLAlchemy()

# ==================== 关联表定义 ====================
# 服务器-用户多对多关联表
server_users = db.Table('server_users',
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True, comment="服务器ID"),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True, comment="用户ID"),
    db.Column('created_at', db.DateTime, default=datetime.now, comment="关联创建时间")
)

class User(db.Model):
    """
    用户表
    存储系统用户信息，包括管理员和普通用户
    普通用户主要用于告警邮件发送，不需要登录功能
    """
    __tablename__ = "users"
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 用户基本信息
    username = db.Column(db.String(50), unique=True, nullable=False, comment="用户名，唯一")
    password = db.Column(db.String(255), nullable=False, comment="密码，已加密")
    email = db.Column(db.String(100), nullable=False, comment="邮箱地址，用于告警通知")
    role = db.Column(db.Enum('admin', 'user'), default='user', comment="用户角色：admin管理员，user普通用户")
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系：一个用户可以有多个服务器（多对多关系）
    servers = db.relationship('Server', secondary=server_users, backref='users', lazy=True)
    
    def keys(self):
        """
        返回字典序列化时的键列表
        用于支持 dict(user) 操作
        """
        return ("id", "username", "email", "role", "created_at")
    
    def __getitem__(self, key):
        """
        支持字典式访问对象属性
        自动处理时间字段的字符串转换
        """
        if key == "created_at":
            return str(getattr(self, key))
        return getattr(self, key)
    
    @classmethod
    def create(cls, username, password, email, role='user'):
        """
        创建新用户
        
        Args:
            username (str): 用户名
            password (str): 密码（已加密）
            email (str): 邮箱地址
            role (str): 用户角色，默认为'user'
            
        Returns:
            User: 创建的用户对象
        """
        user = cls(
            username=username,
            password=password,
            email=email,
            role=role
        )
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def get_all(cls):
        """
        获取所有用户列表
        
        Returns:
            List[User]: 所有用户对象列表
        """
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, user_id):
        """
        根据用户ID获取用户
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            User: 用户对象，如果不存在返回None
        """
        return cls.query.get(user_id)
    
    @classmethod
    def get_by_username(cls, username):
        """
        根据用户名获取用户
        
        Args:
            username (str): 用户名
            
        Returns:
            User: 用户对象，如果不存在返回None
        """
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def update(cls, user_id, **kwargs):
        """
        更新用户信息
        
        Args:
            user_id (int): 用户ID
            **kwargs: 要更新的字段和值
            
        Returns:
            User: 更新后的用户对象，如果用户不存在返回None
            
        示例:
            User.update(1, username='new_username', email='new@example.com')
            User.update(1, password='new_password')
        """
        user = cls.query.get(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key) and key != 'id':  # 不允许修改ID
                    setattr(user, key, value)
            db.session.commit()
            return user
        return None
    
    
    @classmethod
    def delete(cls, user_id):
        """
        删除用户
        
        注意：删除用户前会先解除所有服务器关联关系
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            bool: 删除成功返回True，用户不存在返回False
        """
        user = cls.query.get(user_id)
        if user:
            # 先解除所有服务器关联关系
            for server in user.servers:
                server.users.remove(user)
            
            # 删除用户
            db.session.delete(user)
            db.session.commit()
            return True
        return False
    

class Server(db.Model):
    """
    服务器表
    存储被监控的服务器信息
    每个服务器可以关联多个用户，用于告警邮件发送
    """
    __tablename__ = "servers"
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 服务器基本信息
    server_name = db.Column(db.String(100), nullable=False, comment="服务器名称")
    ip_address = db.Column(db.String(45), unique=True, nullable=False, comment="服务器IP地址，支持IPv4和IPv6")
    port = db.Column(db.Integer, default=22, comment="SSH端口，默认22")
    
    # 移除主要联系人字段，简化为纯多对多关系
    
    # 状态信息已删除
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系：一个服务器可以有多个监控数据记录
    monitor_data = db.relationship('MonitorData', backref='server', lazy=True)
    
    def keys(self):
        """
        返回字典序列化时的键列表
        用于支持 dict(server) 操作
        """
        return ("id", "server_name", "ip_address", "port", "created_at")
    
    def __getitem__(self, key):
        """
        支持字典式访问对象属性
        自动处理时间字段的字符串转换
        """
        if key == "created_at":
            return str(getattr(self, key))
        return getattr(self, key)
    
    @classmethod
    def create(cls, server_name, ip_address, port, user_ids=None):
        """
        创建新服务器
        
        Args:
            server_name (str): 服务器名称
            ip_address (str): 服务器IP地址
            port (int): SSH端口
            user_ids (list, optional): 关联的用户ID列表
            
        Returns:
            Server: 创建的服务器对象
        """
        server = cls(
            server_name=server_name,
            ip_address=ip_address,
            port=port
        )
        db.session.add(server)
        db.session.flush()  # 获取服务器ID
        
        # 关联多个用户
        if user_ids:
            for user_id in user_ids:
                user = User.get_by_id(user_id)
                if user:
                    server.users.append(user)
        
        db.session.commit()
        return server
    
    @classmethod
    def get_all(cls):
        """
        获取所有服务器列表
        
        Returns:
            List[Server]: 所有服务器对象列表
        """
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, server_id):
        """
        根据服务器ID获取服务器
        
        Args:
            server_id (int): 服务器ID
            
        Returns:
            Server: 服务器对象，如果不存在返回None
        """
        return cls.query.get(server_id)
    
    @classmethod
    def get_by_ip(cls, ip_address):
        """
        根据IP地址获取服务器
        
        Args:
            ip_address (str): 服务器IP地址
            
        Returns:
            Server: 服务器对象，如果不存在返回None
        """
        return cls.query.filter_by(ip_address=ip_address).first()
    
    @classmethod
    def get_by_user(cls, user_id):
        """
        获取指定用户的所有服务器
        
        Args:
            user_id (int): 用户ID
            
        Returns:
            List[Server]: 该用户的服务器列表
        """
        # 通过多对多关系查询
        return cls.query.join(server_users).filter(server_users.c.user_id == user_id).all()
    
    @classmethod
    def delete(cls, server_id):
        """
        删除服务器
        
        注意：删除服务器前会先删除所有关联的监控数据
        
        Args:
            server_id (int): 服务器ID
            
        Returns:
            bool: 删除成功返回True，服务器不存在返回False
        """
        server = cls.query.get(server_id)
        if server:
            # 先删除所有关联的监控数据
            MonitorData.query.filter_by(server_id=server_id).delete()
            
            # 删除服务器（会自动解除用户关联关系）
            db.session.delete(server)
            db.session.commit()
            return True
        return False
    
    
    
    def get_alert_users(self):
        """
        获取告警用户列表
        返回所有关联的用户
        
        Returns:
            List[User]: 告警用户列表
        """
        return list(self.users)
    
    @classmethod
    def update_users(cls, server_id, user_ids):
        """
        更新服务器关联用户
        
        Args:
            server_id (int): 服务器ID
            user_ids (list): 关联的用户ID列表
            
        Returns:
            Server: 更新后的服务器对象，如果服务器不存在返回None
            
        示例:
            Server.update_users(1, [1, 2, 3])  # 更新关联用户
            Server.update_users(1, [])  # 清空所有关联用户
        """
        server = cls.query.get(server_id)
        if server:
            # 清空现有关联
            server.users.clear()
            # 添加新的关联用户
            if user_ids:
                for user_id in user_ids:
                    user = User.get_by_id(user_id)
                    if user:
                        server.users.append(user)
            
            db.session.commit()
            return server
        return None
    

class MonitorData(db.Model):
    """
    监控数据表
    存储服务器的CPU、内存、磁盘使用率数据
    支持自定义告警阈值，实现智能告警
    """
    __tablename__ = "monitor_data"
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # 外键关联
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, comment="关联的服务器ID")
    
    # IP地址（冗余存储，提高查询效率）
    ip_address = db.Column(db.String(45), nullable=False, comment="服务器IP地址")
    
    # 监控数据
    cpu_value = db.Column(db.DECIMAL(5, 2), nullable=False, comment="CPU使用率，保留2位小数")
    memory_value = db.Column(db.DECIMAL(5, 2), nullable=False, comment="内存使用率，保留2位小数")
    disk_value = db.Column(db.DECIMAL(5, 2), nullable=False, comment="磁盘使用率，保留2位小数")
    
    # 时间戳
    recorded_at = db.Column(db.DateTime, default=datetime.now, comment="数据记录时间")
    
    def keys(self):
        """
        返回字典序列化时的键列表
        用于支持 dict(monitor_data) 操作
        """
        return ("id", "server_id", "ip_address", "cpu_value", "memory_value", "disk_value", "recorded_at")
    
    def __getitem__(self, key):
        """
        支持字典式访问对象属性
        自动处理时间字段的字符串转换和Decimal类型转换
        """
        value = getattr(self, key)
        
        # 处理时间字段
        if key == "recorded_at":
            return str(value)
        
        # 处理Decimal类型字段
        decimal_fields = ("cpu_value", "memory_value", "disk_value")
        
        if key in decimal_fields:
            if value is not None:
                return float(value)
        
        return value
    
    @classmethod
    def create(cls, server_id, ip_address, cpu_value, memory_value, disk_value):
        """
        创建监控数据记录（包含所有指标）
        
        Args:
            server_id (int): 服务器ID
            ip_address (str): 服务器IP地址
            cpu_value (float): CPU使用率
            memory_value (float): 内存使用率
            disk_value (float): 磁盘使用率
            
        Returns:
            MonitorData: 创建的监控数据对象
        """
        data = cls(
            server_id=server_id,
            ip_address=ip_address,
            cpu_value=cpu_value,
            memory_value=memory_value,
            disk_value=disk_value
        )
        db.session.add(data)
        db.session.commit()
        return data
    
    @classmethod
    def get_latest_by_server(cls, server_id):
        """
        获取服务器最新监控数据
        
        Args:
            server_id (int): 服务器ID
            
        Returns:
            MonitorData: 最新的监控数据对象，如果不存在返回None
        """
        return cls.query.filter_by(server_id=server_id).order_by(cls.recorded_at.desc()).first()
    
    
    @classmethod
    def create_by_ip(cls, ip_address, cpu_value, memory_value, disk_value):
        """
        根据IP地址创建监控数据记录（包含所有指标）
        
        Args:
            ip_address (str): 服务器IP地址
            cpu_value (float): CPU使用率
            memory_value (float): 内存使用率
            disk_value (float): 磁盘使用率
            
        Returns:
            MonitorData: 创建的监控数据对象
            
        Raises:
            ValueError: 当服务器不存在时抛出异常
        """
        # 先根据IP查找服务器
        server = Server.get_by_ip(ip_address)
        if not server:
            raise ValueError(f"服务器 {ip_address} 不存在")
        
        # 创建监控数据
        return cls.create(server.id, ip_address, cpu_value, memory_value, disk_value)
    
    @classmethod
    def get_by_ip(cls, ip_address, start_time):
        """
        根据IP地址查询指定时间范围的数据
        
        Args:
            ip_address (str): 服务器IP地址
            start_time (datetime): 开始时间
            
        Returns:
            List[MonitorData]: 监控数据列表
        """
        server = Server.get_by_ip(ip_address)
        if not server:
            return []
        
        return cls.query.filter(
            cls.server_id == server.id,
            cls.recorded_at >= start_time
        ).order_by(cls.recorded_at.desc()).all()
    
    @classmethod
    def delete_old_data(cls, days=7):
        """
        删除指定天数之前的旧数据
        用于数据清理，避免数据库过大
        
        Args:
            days (int): 保留最近多少天的数据，默认7天
        """
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        cls.query.filter(cls.recorded_at < cutoff_date).delete()
        db.session.commit()
