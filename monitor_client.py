#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控数据采集客户端

功能说明：
- 使用psutil库采集系统CPU、内存、磁盘使用率数据
- 批量提交多类监控数据，提高效率
- 基于IP地址自动匹配服务器记录
- 支持API密钥认证和自动重试机制

使用方法：
1. 基本使用：python monitor_client.py
2. 指定API地址：python monitor_client.py <api_url>
3. 完整配置：python monitor_client.py <api_url> <api_key> <interval> [ip_address]

注意：
- 系统会自动获取本机IP地址，用于匹配数据库中的服务器
- 需要先在数据库中创建对应IP地址的服务器记录
- 支持批量数据提交，一次请求包含CPU、内存、磁盘数据

依赖安装：
pip install psutil requests
"""

import psutil  # 系统监控库
import requests  # HTTP请求库
import time  # 时间处理
import json  # JSON数据处理
import sys  # 系统相关
import os  # 操作系统接口
from datetime import datetime  # 日期时间处理
import logging

# ==================== 日志配置 ====================
# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class MonitorClient:
    """
    监控数据采集客户端
    
    主要功能：
    1. 采集系统CPU、内存、磁盘使用率
    2. 通过HTTP API提交数据到监控系统
    3. 支持定时采集和错误重试
    4. 记录详细的日志信息
    """
    
    def __init__(self, api_url, api_key=None, collect_interval=30, ip_address=None):
        """
        初始化监控客户端
        
        Args:
            api_url (str): API服务器地址，如 http://192.168.1.100:8000
            api_key (str, optional): API密钥，用于身份验证
            collect_interval (int): 采集间隔（秒），默认30秒
            ip_address (str, optional): 服务器IP地址，用于匹配数据库中的服务器
        """
        self.api_url = api_url.rstrip('/')  # API地址，去除末尾斜杠
        self.api_key = api_key  # API密钥
        self.collect_interval = collect_interval  # 采集间隔
        self.ip_address = ip_address or self._get_local_ip()  # 服务器IP地址
        self.running = False  # 运行状态标志
        # 移除硬编码的server_id，让后端根据IP地址自动匹配服务器
        
        # 显示获取到的IP地址
        logger.info(f"检测到的服务器IP: {self.ip_address}")
        
        # 验证API连接
        self._test_connection()
    
    def _get_local_ip(self):
        """获取本地IP地址"""
        try:
            import socket
            import subprocess
            
            # 方法1: 尝试获取网络接口的IP地址
            try:
                # 使用ip命令获取IP地址（Linux系统）
                result = subprocess.run(['ip', 'route', 'get', '8.8.8.8'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # 解析输出获取源IP
                    for line in result.stdout.split('\n'):
                        if 'src' in line:
                            ip = line.split('src')[1].strip().split()[0]
                            if ip and not ip.startswith('127.'):
                                return ip
            except:
                pass
            
            # 方法2: 使用socket连接获取IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            
            # 如果获取到的是127.0.0.1，尝试其他方法
            if ip == "127.0.0.1":
                # 方法3: 获取所有网络接口的IP
                import netifaces
                for interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        for addr in addrs[netifaces.AF_INET]:
                            ip = addr['addr']
                            if not ip.startswith('127.') and not ip.startswith('169.254.'):
                                return ip
            else:
                return ip
                
        except Exception as e:
            print(f"获取IP地址失败: {e}")
            
        # 如果所有方法都失败，返回默认值
        return "127.0.0.1"
    
    def _test_connection(self):
        """测试API连接"""
        try:
            # 测试API根路径 - 移除/api前缀，直接访问/home
            base_url = self.api_url.replace('/api', '')
            response = requests.get(f"{base_url}/home", timeout=5)
            if response.status_code == 200:
                logger.info("✅ API连接成功")
            else:
                logger.warning(f"API响应异常: {response.status_code}")
        except Exception as e:
            logger.error(f"❌ API连接失败: {e}")
            logger.info("请确保Flask服务器正在运行，并且API地址正确")
            sys.exit(1)
    
    def collect_cpu(self):
        """采集CPU使用率"""
        try:
            # 获取1秒内的CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            return round(cpu_percent, 2)
        except Exception as e:
            logger.error(f"CPU数据采集失败: {e}")
            return None
    
    def collect_memory(self):
        """采集内存使用率"""
        try:
            memory = psutil.virtual_memory()
            return round(memory.percent, 2)
        except Exception as e:
            logger.error(f"内存数据采集失败: {e}")
            return None
    
    def collect_disk(self, path='/'):
        """采集磁盘使用率"""
        try:
            # Windows系统使用C盘
            if os.name == 'nt':
                path = 'C:\\'
            
            disk = psutil.disk_usage(path)
            usage_percent = (disk.used / disk.total) * 100
            return round(usage_percent, 2)
        except Exception as e:
            logger.error(f"磁盘数据采集失败: {e}")
            return None
    
    
    def send_batch_data(self, metrics):
        """
        批量发送监控数据到API
        
        Args:
            metrics (dict): 指标数据字典，格式如 {"cpu": 85.5, "memory": 75.2, "disk": 60.1}
            
        Returns:
            bool: 发送是否成功
        """
        if not metrics:
            return False
            
        data = {
            "metrics": metrics,
            "ip_address": self.ip_address
        }
        
        # 调试信息：显示提交的IP地址
        logger.info(f"提交数据 - 使用IP地址: {self.ip_address}")
        
        # 不再提交server_id，让后端根据IP地址自动匹配服务器
        
        try:
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['X-API-Key'] = self.api_key
                
            response = requests.post(
                f"{self.api_url}/monitor/data",
                json=data,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    logger.info(f"批量数据发送成功: {list(metrics.keys())}")
                    return True
                else:
                    logger.error(f"批量数据发送失败: {result.get('message')}")
                    return False
            else:
                logger.error(f"批量数据发送失败: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"批量数据发送超时")
            return False
        except requests.exceptions.ConnectionError:
            logger.error(f"批量数据发送连接错误")
            return False
        except Exception as e:
            logger.error(f"批量数据发送异常: {e}")
            return False
    
    def collect_and_send(self):
        """采集并发送所有监控数据"""
        # 采集所有数据
        metrics = {}
        
        # 采集CPU数据
        cpu_value = self.collect_cpu()
        if cpu_value is not None:
            metrics["cpu"] = cpu_value
        
        # 采集内存数据
        memory_value = self.collect_memory()
        if memory_value is not None:
            metrics["memory"] = memory_value
        
        # 采集磁盘数据
        disk_value = self.collect_disk()
        if disk_value is not None:
            metrics["disk"] = disk_value
        
        # 批量发送数据
        if metrics:
            self.send_batch_data(metrics)
    
    def run(self):
        """运行监控客户端"""
        logger.info(f"监控客户端启动 - 服务器IP: {self.ip_address}, 采集间隔: {self.collect_interval}秒")
        
        self.running = True
        
        try:
            while self.running:
                start_time = time.time()
                
                # 采集并发送数据
                self.collect_and_send()
                
                # 计算剩余等待时间
                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.collect_interval - elapsed_time)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    logger.warning("采集耗时超过间隔时间，立即进行下次采集")
                    
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭监控客户端...")
            self.stop()
        except Exception as e:
            logger.error(f"监控客户端运行异常: {e}")
            self.stop()
    
    def stop(self):
        """停止监控客户端"""
        self.running = False
        logger.info("监控客户端已停止")
    

def main():
    """主函数"""
    # 配置参数
    API_URL = "http://192.168.1.11:8000/api"  # API服务器地址
    API_KEY = "dev-api-key-123456"  # API密钥
    COLLECT_INTERVAL = 30  # 采集间隔（秒）
    IP_ADDRESS = None  # 服务器IP地址（可选）
    
    # 从命令行参数获取配置
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
    if len(sys.argv) > 2:
        API_KEY = sys.argv[2]
    if len(sys.argv) > 3:
        COLLECT_INTERVAL = int(sys.argv[3])
    if len(sys.argv) > 4:
        IP_ADDRESS = sys.argv[4]
    
    # 创建并运行监控客户端
    client = MonitorClient(API_URL, API_KEY, COLLECT_INTERVAL, IP_ADDRESS)
    
    # 显示服务器IP
    logger.info(f"服务器IP: {client.ip_address}")
    
    # 运行监控客户端
    client.run()

if __name__ == "__main__":
    main()
