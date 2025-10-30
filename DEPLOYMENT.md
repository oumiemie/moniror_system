# 监控系统部署指南

## 📋 系统要求

- **操作系统**: Linux (推荐CentOS 7.9+)
- **内存**: 至少 2GB
- **磁盘**: 至少 10GB 可用空间
- **网络**: 能够访问互联网

## 🚀 快速部署

### 1. 准备环境

```bash
# 安装Docker
curl -fsSL https://get.docker.com | bash
sudo systemctl start docker
sudo systemctl enable docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```

### 2. 构建镜像

```bash
# 克隆项目
git clone https://gitee.com/flask-project/moniter.git
cd moniter

# 构建镜像
chmod +x build.sh
./build.sh
```

### 3. 配置环境变量

```bash
# 复制配置文件
cp env.production.example .env

# 编辑配置文件
vim .env
```

### 4. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

## 🔧 详细配置

### 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `FLASK_ENV` | Flask环境 | production |
| `DEBUG` | 调试模式 | false |
| `DATABASE_URL` | 数据库连接 | sqlite:///monitor_production.db |
| `JWT_SECRET_KEY` | JWT密钥 | 必须修改 |
| `API_KEY` | API密钥 | 必须修改 |
| `MAIL_SERVER` | 邮件服务器 | smtp.gmail.com |
| `MAIL_USERNAME` | 邮件用户名 | 必须设置 |
| `MAIL_PASSWORD` | 邮件密码 | 必须设置 |
| `LOG_LEVEL` | 日志级别 | INFO |
| `MONITOR_INTERVAL` | 监控间隔(秒) | 30 |
| `DATA_RETENTION_DAYS` | 数据保留天数 | 30 |

### 生成安全密钥

```bash
# 生成JWT密钥
openssl rand -hex 32

# 生成API密钥
openssl rand -hex 16

# 生成SECRET_KEY
openssl rand -hex 32
```

## 📦 服务管理

### 基本操作

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 更新服务

```bash
# 重新构建镜像
./build.sh

# 重启服务
docker-compose down
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 查看端口占用
sudo netstat -tulpn | grep :80
sudo netstat -tulpn | grep :8000

# 杀死占用进程
sudo kill -9 <PID>
```

#### 2. 权限问题
```bash
# 修复目录权限
sudo chown -R $USER:$USER data/ logs/
chmod 755 data/ logs/
```

#### 3. 数据库问题
```bash
# 重新初始化数据库
docker-compose exec backend python init_db.py
```

#### 4. 网络问题
```bash
# 检查网络连接
docker-compose exec backend ping google.com
docker-compose exec frontend ping google.com
```

### 日志分析

```bash
# 查看所有服务日志
docker-compose logs

# 查看错误日志
docker-compose logs | grep ERROR

# 查看访问日志
docker-compose logs frontend | grep "GET\|POST"
```

## 📊 监控和维护

### 系统监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
du -sh data/ logs/

# 查看系统资源
htop
free -h
df -h
```

### 数据备份

```bash
# 创建备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/monitor-$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# 备份数据目录
tar -czf $BACKUP_DIR/data.tar.gz data/

# 备份日志
tar -czf $BACKUP_DIR/logs.tar.gz logs/

# 备份配置文件
cp .env $BACKUP_DIR/
cp docker-compose.yml $BACKUP_DIR/

echo "备份完成: $BACKUP_DIR"
EOF

chmod +x backup.sh

# 设置定时备份
echo "0 2 * * * $(pwd)/backup.sh" | crontab -
```

### 日志轮转

```bash
# 配置logrotate
sudo tee /etc/logrotate.d/monitor <<EOF
$(pwd)/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        docker-compose restart backend
    endscript
}
EOF
```

## 🎯 访问系统

部署完成后，可以通过以下地址访问：

- **前端界面**: http://服务器IP
- **后端API**: http://服务器IP:8000
- **健康检查**: http://服务器IP/health

### 获取服务器IP
```bash
# 方法1
ip addr show | grep inet

# 方法2
hostname -I

# 方法3
curl ifconfig.me
```

## 🔐 安全建议

### 1. 修改默认密钥
```bash
# 编辑.env文件，修改所有默认密钥
vim .env
```

### 2. 配置防火墙
```bash
# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --reload

# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 3. 使用HTTPS
```bash
# 配置SSL证书
# 将证书文件放在certs/目录下
# 修改nginx.conf配置SSL
```

## 📞 技术支持

如果遇到问题：
1. 查看日志：`docker-compose logs -f`
2. 检查状态：`docker-compose ps`
3. 验证配置：`cat .env`
4. 检查端口：`sudo netstat -tulpn | grep -E ':(80|8000)'`

---

**🎊 恭喜！你的监控系统已成功部署！**
