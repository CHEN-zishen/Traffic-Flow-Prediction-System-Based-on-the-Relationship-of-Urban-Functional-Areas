"""城市级交通预测记录模型"""

from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Float,
    String,
    Date,
    DateTime,
    Text,
)
from sqlalchemy.sql import func

from .base import Base


class CityPrediction(Base):
    __tablename__ = "city_predictions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True, index=True, comment='用户ID')
    model_type = Column(String(20), nullable=True, index=True, comment='使用的模型类型：lstm/gru/ml-hgstn/transformer/tcn')
    city = Column(String(64), nullable=False, index=True)
    prediction_date = Column(Date, nullable=False, index=True)
    time_range = Column(String(64), nullable=False)
    weather = Column(String(32), nullable=True)
    district = Column(String(64), nullable=True)
    other = Column(String(255), nullable=True)

    flow_per_hour = Column(Integer, nullable=False)
    avg_speed = Column(Float, nullable=False)
    congestion_index = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)
    index_score = Column(Float, nullable=False)

    extra_payload = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        index=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "model_type": self.model_type,
            "city": self.city,
            "prediction_date": self.prediction_date.isoformat() if self.prediction_date else None,
            "time_range": self.time_range,
            "weather": self.weather,
            "district": self.district,
            "other": self.other,
            "flow_per_hour": self.flow_per_hour,
            "avg_speed": self.avg_speed,
            "congestion_index": self.congestion_index,
            "severity": self.severity,
            "confidence": self.confidence,
            "index_score": self.index_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


