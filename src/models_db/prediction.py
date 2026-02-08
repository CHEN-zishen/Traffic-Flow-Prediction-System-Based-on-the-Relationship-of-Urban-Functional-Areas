"""
预测结果表ORM模型
"""

from sqlalchemy import Column, BigInteger, Integer, Float, String, DateTime, Enum, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base
import enum


class CongestionLevel(enum.Enum):
    """拥堵状态枚举"""
    CLEAR = "畅通"
    SLOW = "缓行"
    CONGESTED = "拥堵"


class Prediction(Base):
    """预测结果表"""
    
    __tablename__ = 'predictions'
    
    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 基本信息
    sensor_id = Column(Integer, nullable=False, index=True, comment='传感器ID')
    prediction_time = Column(DateTime, nullable=False, index=True, comment='预测时间')
    target_time = Column(DateTime, nullable=False, index=True, comment='目标时间')
    
    # 流量预测
    flow_prediction = Column(Float, comment='流量预测值')
    flow_actual = Column(Float, default=None, comment='实际流量值')
    
    # 密度预测
    density_prediction = Column(Float, comment='密度预测值')
    density_actual = Column(Float, default=None, comment='实际密度值')
    
    # 拥堵状态预测
    congestion_prediction = Column(
        Enum('畅通', '正常', '拥堵', '严重拥堵', name='congestion_enum'),
        comment='拥堵状态预测'
    )
    congestion_actual = Column(
        Enum('畅通', '正常', '拥堵', '严重拥堵', name='congestion_enum'),
        default=None,
        comment='实际拥堵状态'
    )
    
    # 其他信息
    confidence = Column(Float, comment='预测置信度')
    model_version = Column(String(50), index=True, comment='使用的模型版本')
    
    # 时间戳
    created_at = Column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        comment='创建时间'
    )
    
    def __repr__(self):
        return (f"<Prediction(id={self.id}, sensor_id={self.sensor_id}, "
                f"target_time={self.target_time}, "
                f"flow={self.flow_prediction:.2f})>")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'sensor_id': self.sensor_id,
            'prediction_time': self.prediction_time.isoformat() if self.prediction_time else None,
            'target_time': self.target_time.isoformat() if self.target_time else None,
            'flow_prediction': self.flow_prediction,
            'flow_actual': self.flow_actual,
            'density_prediction': self.density_prediction,
            'density_actual': self.density_actual,
            'congestion_prediction': self.congestion_prediction,
            'congestion_actual': self.congestion_actual,
            'confidence': self.confidence,
            'model_version': self.model_version,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

