"""
监控数据API接口
支持批量数据提交和IP地址匹配
"""

from flask import request
from flask_restful import Resource
from lib.response import response
from model.models import MonitorData, Server
from model.models import db
from lib.jwt_utils import get_current_user, admin_required
from lib.api_auth import api_key_required
from mail.simple_alert import check_and_send_alert_by_ip
import logging

logger = logging.getLogger(__name__)

class MonitorDataAPI(Resource):
    """监控数据API"""
    
    @api_key_required
    def post(self):
        """提交监控数据（需要API密钥）"""
        try:
            data = request.json
            server_id = data.get('server_id')
            ip_address = data.get('ip_address')
            metrics = data.get('metrics')  # 改为批量提交
            
            # 验证必需字段
            if not metrics:
                return response(message="监控数据不能为空", code=400)
            
            # 获取服务器
            server = None
            if server_id:
                # 优先使用server_id查找
                server = Server.get_by_id(server_id)
            elif ip_address:
                # 根据IP地址查找服务器
                server = Server.get_by_ip(ip_address)
            else:
                return response(message="请提供server_id或ip_address", code=400)
            
            if not server:
                return response(message="服务器不存在", code=400)
            
            # 创建监控数据（包含所有指标）
            try:
                # 支持两种字段名格式：cpu_value/cpu, memory_value/memory, disk_value/disk
                cpu_value = metrics.get('cpu_value', metrics.get('cpu', 0.0))
                memory_value = metrics.get('memory_value', metrics.get('memory', 0.0))
                disk_value = metrics.get('disk_value', metrics.get('disk', 0.0))
                
                # 调试信息：显示提交的IP地址和服务器IP地址
                logger.info(f"客户端提交的IP地址: {ip_address}")
                logger.info(f"数据库中的服务器IP地址: {server.ip_address}")
                
                monitor_data = MonitorData.create_by_ip(
                    server.ip_address, 
                    cpu_value, 
                    memory_value, 
                    disk_value
                )
                
                # 状态字段已删除，不再需要更新状态
                
                logger.info(f"服务器 {server.server_name} ({server.ip_address}) 提交监控数据: CPU={cpu_value}%, 内存={memory_value}%, 磁盘={disk_value}%")
            except ValueError as e:
                return response(message=str(e), code=400)
            
            # 检查告警（统一使用IP地址）
            try:
                # 处理告警检查，支持两种字段名格式
                alert_metrics = {
                    'cpu': cpu_value,
                    'memory': memory_value,
                    'disk': disk_value
                }
                for metric_type, value in alert_metrics.items():
                    check_and_send_alert_by_ip(server.ip_address, metric_type, float(value))
            except Exception as e:
                logger.error(f"告警检查失败: {e}")
            
            return response(message="监控数据提交成功")
            
        except Exception as e:
            logger.error(f"提交监控数据失败: {e}")
            return response(message="提交监控数据失败", code=500)
    
    @admin_required
    def get(self):
        """获取监控数据（仅管理员）"""
        try:
            # 获取查询参数
            server_id = request.args.get('server_id', type=int)
            metric_type = request.args.get('metric_type')
            hours = request.args.get('hours', 24, type=int)
            
            if server_id:
                # 获取指定服务器的数据
                data = MonitorData.get_latest_by_server(server_id)
                if data:
                    data = [data]  # 转换为列表格式
                else:
                    data = []
            else:
                # 获取所有最新数据
                data = []
                servers = Server.get_all()
                for server in servers:
                    latest = MonitorData.get_latest_by_server(server.id)
                    if latest:
                        data.append(latest)
            
            # 转换为字典格式，处理Decimal类型
            data_list = []
            for item in data:
                item_dict = dict(item)
                # 将Decimal类型转换为float
                for field in ['cpu_value', 'memory_value', 'disk_value']:
                    if field in item_dict and item_dict[field] is not None:
                        item_dict[field] = float(item_dict[field])
                data_list.append(item_dict)
            
            return response(data=data_list, message="获取监控数据成功")
            
        except Exception as e:
            logger.error(f"获取监控数据失败: {e}")
            return response(message="获取监控数据失败", code=500)
    

class MonitorStats(Resource):
    """监控统计API（仅管理员）"""
    
    @admin_required
    def get(self):
        """获取监控统计信息（仅管理员）"""
        try:
            # 获取查询参数
            server_id = request.args.get('server_id', type=int)
            hours = request.args.get('hours', 24, type=int)
            
            if server_id:
                servers = [Server.get_by_id(server_id)]
            else:
                servers = Server.get_all()
            
            stats = []
            for server in servers:
                server_stats = {
                    'server_id': server.id,
                    'server_name': server.server_name,
                    'ip_address': server.ip_address,
                    # status字段已删除
                    'users': [dict(user) for user in server.users],  # 多用户关联信息
                    'metrics': {}
                }
                
                # 获取最新监控数据
                latest_data = MonitorData.get_latest_by_server(server.id)
                if latest_data:
                    from config.settings import DEFAULT_THRESHOLDS
                    server_stats['metrics'] = {
                        'cpu': {
                            'value': float(latest_data.cpu_value),
                            'threshold_warning': DEFAULT_THRESHOLDS['cpu']['warning'],
                            'threshold_critical': DEFAULT_THRESHOLDS['cpu']['critical'],
                            'threshold_emergency': DEFAULT_THRESHOLDS['cpu']['emergency'],
                            'recorded_at': str(latest_data.recorded_at)
                        },
                        'memory': {
                            'value': float(latest_data.memory_value),
                            'threshold_warning': DEFAULT_THRESHOLDS['memory']['warning'],
                            'threshold_critical': DEFAULT_THRESHOLDS['memory']['critical'],
                            'threshold_emergency': DEFAULT_THRESHOLDS['memory']['emergency'],
                            'recorded_at': str(latest_data.recorded_at)
                        },
                        'disk': {
                            'value': float(latest_data.disk_value),
                            'threshold_warning': DEFAULT_THRESHOLDS['disk']['warning'],
                            'threshold_critical': DEFAULT_THRESHOLDS['disk']['critical'],
                            'threshold_emergency': DEFAULT_THRESHOLDS['disk']['emergency'],
                            'recorded_at': str(latest_data.recorded_at)
                        }
                    }
                
                stats.append(server_stats)
            
            return response(data=stats, message="获取监控统计成功")
            
        except Exception as e:
            logger.error(f"获取监控统计失败: {e}")
            return response(message="获取监控统计失败", code=500)


