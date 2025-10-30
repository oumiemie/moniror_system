# 企业级服务器监控系统

基于Flask + Vue 3的现代化服务器监控平台，提供实时监控、智能告警、多用户协作等功能。

## 项目概述

本项目是一个企业级服务器监控系统，支持CPU、内存、磁盘使用率的实时监控，具备智能告警、多用户管理、权限控制等核心功能。系统采用前后端分离架构，后端使用Flask提供RESTful API，前端使用Vue 3构建现代化用户界面。

## 技术栈

### 后端技术
- **Flask 2.3.3** - Python Web框架
- **SQLAlchemy** - ORM数据库操作
- **MySQL 5.7** - 关系型数据库
- **Flask-JWT-Extended** - JWT身份认证
- **Flask-Migrate** - 数据库迁移管理
- **psutil** - 系统监控数据采集
- **smtplib** - 邮件告警功能

### 前端技术
- **Vue 3** - 渐进式JavaScript框架
- **Vue Router 4** - 单页面应用路由
- **Pinia** - 状态管理
- **Axios** - HTTP客户端
- **JavaScript** - 现代化的JavaScript开发
- **Vite** - 现代化构建工具

## 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   监控客户端     │    │   监控服务器     │    │   前端界面      │
│  monitor_client │───▶│   Flask API     │◀───│   Vue 3 App     │
│                 │    │                 │    │                 │
│ • 数据采集       │    │ • 数据存储       │    │ • 用户界面      │
│ • 定时上报       │    │ • 智能告警       │    │ • 数据展示      │
│ • IP地址匹配     │    │ • 权限控制       │    │ • 系统管理      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MySQL数据库    │
                       │                 │
                       │ • 用户管理       │
                       │ • 服务器信息     │
                       │ • 监控数据       │
                       │ • 告警记录       │
                       └─────────────────┘
```

## 核心功能

### 1. 实时监控
- **CPU使用率监控** - 实时采集CPU使用情况
- **内存使用率监控** - 监控内存占用情况
- **磁盘使用率监控** - 跟踪磁盘空间使用
- **IP地址匹配** - 根据IP地址自动匹配服务器

### 2. 智能告警
- **阈值告警** - 基于配置的阈值进行告警
- **持续告警检查** - 防止误报的持续监控机制
- **邮件通知** - SMTP邮件告警功能
- **多用户通知** - 支持多个用户接收告警

### 3. 用户管理
- **角色权限控制** - 管理员和普通用户权限分离
- **JWT身份认证** - 安全的Token认证机制
- **密码管理** - 支持密码重置功能
- **多用户协作** - 支持多用户同时使用

### 4. 服务器管理
- **服务器注册** - 手动添加服务器信息
- **用户关联** - 服务器与用户的多对多关联
- **状态监控** - 在线/离线状态跟踪
- **批量管理** - 支持批量操作

## 数据库设计

### 表结构关系图

```
┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│    users    │    │  server_users   │    │   servers   │
│             │    │                 │    │             │
│ id (PK)     │◀───┤ user_id (FK)    │    │ id (PK)     │
│ username    │    │ server_id (FK)  │───▶│ server_name │
│ password    │    │                 │    │ ip_address  │
│ role        │    │                 │    │ port        │
│ created_at  │    │                 │    │ status      │
└─────────────┘    └─────────────────┘    │ created_at  │
                                          └─────────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │  monitor_data   │
                                          │                 │
                                          │ id (PK)         │
                                          │ server_id (FK)  │
                                          │ ip_address      │
                                          │ cpu_value       │
                                          │ memory_value    │
                                          │ disk_value      │
                                          │ recorded_at     │
                                          └─────────────────┘
```

### 表详细设计

#### 1. users 用户表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password | VARCHAR(255) | NOT NULL | 密码(加密) |
| role | ENUM('admin', 'user') | NOT NULL, DEFAULT 'user' | 用户角色 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 2. servers 服务器表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 服务器ID |
| server_name | VARCHAR(100) | NOT NULL | 服务器名称 |
| ip_address | VARCHAR(45) | UNIQUE, NOT NULL | IP地址 |
| port | INT | NOT NULL, DEFAULT 22 | 端口号 |
| status | ENUM('online', 'offline') | NOT NULL, DEFAULT 'offline' | 状态 |
| created_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### 3. server_users 服务器用户关联表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| user_id | INT | FOREIGN KEY, NOT NULL | 用户ID |
| server_id | INT | FOREIGN KEY, NOT NULL | 服务器ID |
| PRIMARY KEY | (user_id, server_id) | | 复合主键 |

#### 4. monitor_data 监控数据表
| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | 数据ID |
| server_id | INT | FOREIGN KEY, NOT NULL | 服务器ID |
| ip_address | VARCHAR(45) | NOT NULL | 服务器IP地址 |
| cpu_value | DECIMAL(5,2) | NOT NULL | CPU使用率(%) |
| memory_value | DECIMAL(5,2) | NOT NULL | 内存使用率(%) |
| disk_value | DECIMAL(5,2) | NOT NULL | 磁盘使用率(%) |
| recorded_at | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 记录时间 |

## API接口文档

### 认证接口

#### 用户登录
- **URL**: `POST /api/auth/login`
- **描述**: 用户登录获取JWT Token
- **请求体**:
  ```json
  {
    "username": "admin",
    "password": "admin123"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "msg": "登录成功",
    "data": {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "user": {
        "id": 1,
        "username": "admin",
        "role": "admin"
      }
    }
  }
  ```

### 用户管理接口

#### 获取用户列表
- **URL**: `GET /api/users`
- **权限**: 仅管理员
- **响应**:
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": [
      {
        "id": 1,
        "username": "admin",
        "role": "admin",
        "created_at": "2024-01-01 00:00:00"
      }
    ]
  }
  ```

#### 添加用户
- **URL**: `POST /api/users`
- **权限**: 仅管理员
- **请求体**:
  ```json
  {
    "username": "newuser",
    "password": "password123",
    "role": "user"
  }
  ```

#### 重置密码
- **URL**: `PUT /api/users/reset-password`
- **权限**: 仅管理员
- **请求体**:
  ```json
  {
    "username": "newuser",
    "password": "newpassword123"
  }
  ```

#### 删除用户
- **URL**: `DELETE /api/users/{user_id}`
- **权限**: 仅管理员

### 服务器管理接口

#### 获取服务器列表
- **URL**: `GET /api/servers`
- **权限**: 需要登录
- **响应**:
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": [
      {
        "id": 1,
        "server_name": "Web服务器",
        "ip_address": "192.168.1.100",
        "port": 22,
        "status": "online",
        "users": [
          {"id": 1, "username": "admin"}
        ],
        "created_at": "2024-01-01 00:00:00"
      }
    ]
  }
  ```

#### 添加服务器
- **URL**: `POST /api/servers`
- **权限**: 需要登录
- **请求体**:
  ```json
  {
    "server_name": "新服务器",
    "ip_address": "192.168.1.101",
    "port": 22,
    "user_ids": [1, 2]
  }
  ```

#### 更新服务器
- **URL**: `PUT /api/servers/{server_id}`
- **权限**: 需要登录
- **请求体**:
  ```json
  {
    "server_name": "更新服务器",
    "ip_address": "192.168.1.101",
    "port": 22,
    "user_ids": [1, 2, 3]
  }
  ```

#### 删除服务器
- **URL**: `DELETE /api/servers/{server_id}`
- **权限**: 需要登录

#### 管理服务器用户
- **URL**: `POST /api/servers/{server_id}/users`
- **权限**: 需要登录
- **请求体**:
  ```json
  {
    "user_ids": [1, 2, 3]
  }
  ```

### 监控数据接口

#### 提交监控数据
- **URL**: `POST /api/monitor/data`
- **权限**: API Key认证
- **请求体**:
  ```json
  {
    "ip_address": "192.168.1.100",
    "metrics": {
      "cpu_value": 45.5,
      "memory_value": 67.8,
      "disk_value": 23.4
    }
  }
  ```

#### 获取监控数据
- **URL**: `GET /api/monitor/data`
- **权限**: 需要登录
- **参数**:
  - `server_id` (可选): 指定服务器ID
- **响应**:
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": [
      {
        "id": 1,
        "server_id": 1,
        "server_name": "Web服务器",
        "ip_address": "192.168.1.100",
        "cpu_value": 45.5,
        "memory_value": 67.8,
        "disk_value": 23.4,
        "recorded_at": "2024-01-01 12:00:00"
      }
    ]
  }
  ```

#### 获取监控统计
- **URL**: `GET /api/monitor/stats`
- **权限**: 需要登录
- **响应**:
  ```json
  {
    "code": 200,
    "msg": "获取成功",
    "data": {
      "total_servers": 5,
      "online_servers": 4,
      "offline_servers": 1,
      "alert_count": 2,
      "latest_data": [
        {
          "server_name": "Web服务器",
          "cpu_value": 45.5,
          "memory_value": 67.8,
          "disk_value": 23.4,
          "recorded_at": "2024-01-01 12:00:00"
        }
      ]
    }
  }
  ```

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### 1. 克隆项目
```bash
git clone https://gitee.com/zhang-tie-tie/flask.git
cd monitor-master
```

### 2. 后端部署
```bash
# 安装Python依赖
pip install -r requirements.txt

# 配置数据库
# 修改 config/settings.py 中的数据库配置

# 初始化数据库
python init_db.py

# 启动后端服务
python start.py
```

### 3. 前端部署
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问系统
- 前端地址: http://localhost:5173
- 后端API: http://localhost:8000
- 默认管理员账号: admin / admin123

## 监控客户端部署

### 1. 安装依赖
```bash
pip install psutil requests
```

### 2. 配置客户端
```python
# 修改 monitor_client.py 中的配置
API_URL = "http://your-server:8000"
API_KEY = "your-api-key"
```

### 3. 运行客户端
```bash
python monitor_client.py
```

## 配置说明

### 环境变量配置
```bash
# 数据库配置
export DB_HOST=localhost
export DB_USER=flask
export DB_PASS=123456
export DB_PORT=3306
export DATABASE=monitor_db

# JWT配置
export JWT_SECRET_KEY=your-secret-key

# 邮件配置
export SMTP_HOST=smtp.qq.com
export SMTP_PORT=587
export SMTP_USER=your-email@qq.com
export SMTP_PASS=your-email-password
```

### 告警阈值配置
在 `config/settings.py` 中配置告警阈值：
```python
DEFAULT_THRESHOLDS = {
    'cpu': {'warning': 70, 'critical': 85},
    'memory': {'warning': 80, 'critical': 90},
    'disk': {'warning': 85, 'critical': 95}
}
```

## 项目结构

```
monitor-master/
├── config/                 # 配置文件
│   └── settings.py        # 系统配置
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── api/          # API接口
│   │   ├── views/        # 页面组件
│   │   ├── stores/       # 状态管理
│   │   └── router/       # 路由配置
│   └── package.json      # 前端依赖
├── lib/                   # 工具库
│   ├── api_auth.py       # API认证
│   ├── jwt_utils.py      # JWT工具
│   └── response.py       # 响应工具
├── mail/                  # 邮件模块
│   └── simple_alert.py   # 告警邮件
├── model/                 # 数据模型
│   └── models.py         # 数据库模型
├── router/                # API路由
│   ├── auth.py           # 认证接口
│   ├── user.py           # 用户接口
│   ├── server.py         # 服务器接口
│   └── monitor.py        # 监控接口
├── migrations/            # 数据库迁移
├── monitor_client.py      # 监控客户端
├── manager.py            # Flask应用入口
├── init_db.py            # 数据库初始化
├── start.py              # 启动脚本
└── requirements.txt      # Python依赖
```

## 开发说明

### 数据库迁移
```bash
# 创建迁移文件
flask db migrate -m "描述"

# 执行迁移
flask db upgrade
```

### 前端构建
```bash
cd frontend
npm run build
```

### 生产部署
```bash
# 使用Gunicorn部署后端
gunicorn -w 4 -b 0.0.0.0:8000 manager:app

# 使用Nginx代理前端
# 配置Nginx指向frontend/dist目录
```

## 许可证

MIT License

## 联系方式

- 项目地址: https://gitee.com/zhang-tie-tie/flask
- 作者: 张铁铁
- 邮箱: your-email@example.com