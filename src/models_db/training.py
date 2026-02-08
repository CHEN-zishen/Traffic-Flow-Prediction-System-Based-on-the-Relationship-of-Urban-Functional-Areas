"""
训练记录表ORM模型
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Enum, Text, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base
import enum


class TrainingStatus(enum.Enum):
    """训练状态枚举"""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class TrainingRecord(Base):
    """训练记录表"""
    
    __tablename__ = 'training_records'
    
    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    
    # 模型信息
    model_name = Column(String(100), nullable=False, comment='模型名称（LSTM/GRU）')
    model_version = Column(String(50), nullable=False, index=True, comment='模型版本号')
    
    # 训练时间
    start_time = Column(DateTime, nullable=False, comment='训练开始时间')
    end_time = Column(DateTime, comment='训练结束时间')
    duration_seconds = Column(Integer, comment='训练时长（秒）')
    
    # 训练参数
    epochs = Column(Integer, comment='训练轮数')
    batch_size = Column(Integer, comment='批大小')
    learning_rate = Column(Float, comment='学习率')
    optimizer = Column(String(50), comment='优化器')
    
    # 训练结果
    train_loss = Column(Float, comment='最终训练损失')
    val_loss = Column(Float, comment='最终验证损失')
    best_epoch = Column(Integer, comment='最佳模型对应的epoch')
    
    # 评估指标
    mae = Column(Float, comment='Mean Absolute Error')
    rmse = Column(Float, comment='Root Mean Square Error')
    mape = Column(Float, comment='Mean Absolute Percentage Error')
    accuracy = Column(Float, comment='分类准确率')
    
    # 模型文件
    model_path = Column(String(255), comment='模型文件路径')
    config_json = Column(Text, comment='完整配置（JSON格式）')
    
    # 状态
    status = Column(
        Enum('running', 'completed', 'failed', 'stopped', name='training_status_enum'),
        default='running',
        index=True,
        comment='训练状态'
    )
    notes = Column(Text, comment='备注')
    
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
        return (f"<TrainingRecord(id={self.id}, model={self.model_name}, "
                f"version={self.model_version}, status={self.status})>")
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'learning_rate': self.learning_rate,
            'optimizer': self.optimizer,
            'train_loss': self.train_loss,
            'val_loss': self.val_loss,
            'best_epoch': self.best_epoch,
            'mae': self.mae,
            'rmse': self.rmse,
            'mape': self.mape,
            'accuracy': self.accuracy,
            'model_path': self.model_path,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

