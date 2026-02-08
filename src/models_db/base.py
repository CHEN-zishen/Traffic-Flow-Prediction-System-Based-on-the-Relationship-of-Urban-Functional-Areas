"""
SQLAlchemy ORM 基础模型
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional

# 创建基础模型类
Base = declarative_base()


class DatabaseConnection:
    """数据库连接管理类（单例模式）"""
    
    _instance: Optional['DatabaseConnection'] = None
    _engine = None
    _SessionLocal = None
    
    def __new__(cls, database_url: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, database_url: str = None):
        """
        初始化数据库连接
        
        Args:
            database_url: 数据库连接URL
        """
        if self._engine is None and database_url:
            self._initialize(database_url)
    
    def _initialize(self, database_url: str):
        """初始化数据库引擎和会话"""
        # 创建引擎
        self._engine = create_engine(
            database_url,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
            future=True
        )
        
        # 创建会话工厂
        self._SessionLocal = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            future=True
        )
    
    @property
    def engine(self):
        """获取数据库引擎"""
        return self._engine
    
    @property
    def SessionLocal(self):
        """获取会话工厂"""
        return self._SessionLocal
    
    def get_session(self):
        """
        获取数据库会话
        
        Returns:
            SQLAlchemy会话对象
        """
        if self._SessionLocal is None:
            raise RuntimeError("数据库未初始化，请先调用初始化方法")
        return self._SessionLocal()
    
    def create_all_tables(self):
        """创建所有表"""
        if self._engine is None:
            raise RuntimeError("数据库引擎未初始化")
        Base.metadata.create_all(bind=self._engine)
    
    def drop_all_tables(self):
        """删除所有表（谨慎使用）"""
        if self._engine is None:
            raise RuntimeError("数据库引擎未初始化")
        Base.metadata.drop_all(bind=self._engine)
    
    def close(self):
        """关闭数据库连接"""
        if self._engine:
            self._engine.dispose()


# 全局数据库连接实例
db_connection = DatabaseConnection()


def init_database(database_url: str):
    """
    初始化数据库
    
    Args:
        database_url: 数据库连接URL
    """
    global db_connection
    db_connection = DatabaseConnection(database_url)
    return db_connection


def get_db():
    """
    获取数据库会话（用于依赖注入）
    
    Yields:
        数据库会话
    """
    session = db_connection.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

