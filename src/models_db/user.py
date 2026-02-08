"""用户数据模型"""
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Text, Boolean, Float
from datetime import datetime
from .base import Base
import json


class User(Base):
    """用户表模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment='用户ID')
    username = Column(String(50), unique=True, nullable=False, index=True, comment='用户名')
    email = Column(String(100), unique=True, nullable=False, index=True, comment='邮箱')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    nickname = Column(String(50), comment='昵称')
    avatar = Column(String(255), comment='头像URL')
    role = Column(String(20), default='user', comment='角色：admin/user')
    status = Column(SmallInteger, default=1, index=True, comment='状态：1-正常，0-禁用')
    last_login_time = Column(DateTime, comment='最后登录时间')
    last_login_ip = Column(String(50), comment='最后登录IP')
    login_count = Column(Integer, default=0, comment='登录次数')
    prediction_count = Column(Integer, default=0, comment='预测次数')
    
    # 模型配置相关
    model_type = Column(String(20), default='lstm', comment='选择的模型类型：lstm/gru/ml-hgstn/transformer/tcn')
    weather_sensitivity = Column(Float, default=0.5, comment='天气因素敏感度（0-1，0.5为适中）')
    time_sensitivity = Column(Float, default=0.5, comment='时间段因素敏感度（0-1，0.5为适中）')
    district_sensitivity = Column(Float, default=0.5, comment='城市功能区因素敏感度（0-1，0.5为适中）')
    other_sensitivity = Column(Float, default=0.5, comment='其他因素敏感度（0-1，0.5为适中）')
    use_gpu = Column(Boolean, default=False, comment='是否使用GPU加速')
    multi_predict = Column(Boolean, default=False, comment='是否多次预测')
    
    # 账号设置
    receive_email = Column(Boolean, default=True, comment='是否接收邮件通知')
    
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self, include_sensitive=False):
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'role': self.role,
            'status': self.status,
            'last_login_time': self.last_login_time.isoformat() if self.last_login_time else None,
            'last_login_ip': self.last_login_ip,
            'login_count': self.login_count,
            'prediction_count': self.prediction_count,
            'model_type': self.model_type,
            'weather_sensitivity': self.weather_sensitivity,
            'time_sensitivity': self.time_sensitivity,
            'district_sensitivity': self.district_sensitivity,
            'other_sensitivity': self.other_sensitivity,
            'use_gpu': self.use_gpu,
            'multi_predict': self.multi_predict,
            'receive_email': self.receive_email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"

