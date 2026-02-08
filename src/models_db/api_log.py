"""
API日志表ORM模型
"""

from sqlalchemy import Column, BigInteger, Integer, Float, String, Text, DateTime, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base


class APILog(Base):
    """API调用日志表"""
    
    __tablename__ = 'api_logs'
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 请求信息
    endpoint = Column(String(255), nullable=False, index=True, comment='API端点')
    method = Column(String(10), nullable=False, comment='HTTP方法')
    request_ip = Column(String(50), comment='请求IP')
    request_params = Column(Text, comment='请求参数（JSON）')
    
    # 响应信息
    response_status = Column(Integer, index=True, comment='响应状态码')
    response_time_ms = Column(Integer, comment='响应时间（毫秒）')
    error_message = Column(Text, comment='错误信息（如有）')
    
    # 时间戳
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        index=True,
        comment='创建时间'
    )
    
    def __repr__(self):
        return (f"<APILog(id={self.id}, endpoint={self.endpoint}, "
                f"method={self.method}, status={self.response_status})>")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'endpoint': self.endpoint,
            'method': self.method,
            'request_ip': self.request_ip,
            'request_params': self.request_params,
            'response_status': self.response_status,
            'response_time_ms': self.response_time_ms,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ModelPerformance(Base):
    """模型性能对比表"""
    
    __tablename__ = 'model_performance'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 模型信息
    model_name = Column(String(100), nullable=False, index=True, comment='模型名称')
    model_version = Column(String(50), nullable=False, comment='模型版本')
    test_dataset = Column(String(100), comment='测试数据集')
    
    # 性能指标
    metric_name = Column(String(50), nullable=False, index=True, comment='指标名称')
    metric_value = Column(Float, nullable=False, comment='指标值')
    
    # 评估时间
    evaluation_time = Column(DateTime, nullable=False, index=True, comment='评估时间')
    
    # 时间戳
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        comment='创建时间'
    )
    
    def __repr__(self):
        return (f"<ModelPerformance(model={self.model_name}, "
                f"metric={self.metric_name}, value={self.metric_value})>")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'test_dataset': self.test_dataset,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'evaluation_time': self.evaluation_time.isoformat() if self.evaluation_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SystemConfig(Base):
    """系统配置表"""
    
    __tablename__ = 'system_config'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 配置信息
    config_key = Column(String(100), nullable=False, unique=True, index=True, comment='配置键')
    config_value = Column(Text, comment='配置值')
    config_type = Column(String(50), comment='配置类型')
    description = Column(String(255), comment='配置说明')
    is_active = Column(Boolean, default=True, index=True, comment='是否启用')
    
    # 时间戳
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        comment='创建时间'
    )
    updated_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        comment='更新时间'
    )
    
    def __repr__(self):
        return f"<SystemConfig(key={self.config_key}, value={self.config_value})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

