"""
数据库初始化脚本
创建数据库和表结构
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import get_database_url, config
from src.models_db.base import init_database, Base
from src.models_db.prediction import Prediction
from src.models_db.training import TrainingRecord
from src.models_db.api_log import APILog, ModelPerformance, SystemConfig
from src.models_db.city_prediction import CityPrediction  # noqa: F401


def create_database():
    """创建数据库（如果不存在）"""
    import pymysql
    from dotenv import load_dotenv
    
    # 加载环境变量
    load_dotenv()
    
    # 获取数据库配置
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', 3306))
    database = os.getenv('MYSQL_DATABASE', 'traffic_db')
    
    try:
        # 连接到MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS {database} "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print(f"✅ 数据库 '{database}' 创建成功（或已存在）")
        
        connection.close()
        return True
    
    except Exception as e:
        print(f"❌ 数据库创建失败: {e}")
        return False


def create_tables():
    """使用SQLAlchemy创建所有表"""
    try:
        # 获取数据库URL
        database_url = get_database_url()
        print(f"📍 连接数据库: {database_url.split('@')[1]}")  # 隐藏密码
        
        # 初始化数据库连接
        db_conn = init_database(database_url)
        
        # 创建所有表
        print("🔨 开始创建数据库表...")
        db_conn.create_all_tables()
        print("✅ 所有表创建成功")
        
        # 验证表是否创建成功
        from sqlalchemy import inspect
        inspector = inspect(db_conn.engine)
        tables = inspector.get_table_names()
        
        print(f"\n📋 已创建的表 ({len(tables)}个):")
        for table in tables:
            print(f"  - {table}")
        
        return True
    
    except Exception as e:
        print(f"❌ 表创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def initialize_config():
    """初始化系统配置"""
    from src.utils.db_utils import get_db_manager
    
    try:
        db_manager = get_db_manager()
        
        # 初始化默认配置
        configs = [
            ('system.version', '1.0.0', '系统版本'),
            ('model.default_version', 'lstm_v1.0', '默认模型版本'),
            ('prediction.batch_limit', '1000', '预测批量限制'),
            ('api.rate_limit', '100', 'API速率限制（请求/分钟）'),
        ]
        
        print("\n⚙️  初始化系统配置...")
        for key, value, desc in configs:
            db_manager.set_config(key, value, desc)
            print(f"  ✓ {key} = {value}")
        
        print("✅ 系统配置初始化完成")
        return True
    
    except Exception as e:
        print(f"❌ 配置初始化失败: {e}")
        return False


def run_sql_script():
    """（可选）直接运行SQL脚本"""
    import pymysql
    from dotenv import load_dotenv
    
    load_dotenv()
    
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    host = os.getenv('MYSQL_HOST', 'localhost')
    port = int(os.getenv('MYSQL_PORT', 3306))
    database = os.getenv('MYSQL_DATABASE', 'traffic_db')
    
    sql_file = project_root / 'database' / 'init.sql'
    
    if not sql_file.exists():
        print(f"⚠️  SQL脚本不存在: {sql_file}")
        return False
    
    try:
        print(f"\n📄 执行SQL脚本: {sql_file}")
        
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 分割SQL语句
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        
        with connection.cursor() as cursor:
            for statement in statements:
                if statement:
                    try:
                        cursor.execute(statement)
                    except Exception as e:
                        # 某些语句可能失败（如表已存在），继续执行
                        pass
        
        connection.commit()
        connection.close()
        
        print("✅ SQL脚本执行完成")
        return True
    
    except Exception as e:
        print(f"❌ SQL脚本执行失败: {e}")
        return False


def test_connection():
    """测试数据库连接"""
    try:
        from src.utils.db_utils import get_db_manager
        
        print("\n🔍 测试数据库连接...")
        db_manager = get_db_manager()
        
        # 尝试查询系统配置
        version = db_manager.get_config('system.version')
        if version:
            print(f"✅ 数据库连接正常，系统版本: {version}")
            return True
        else:
            print("⚠️  数据库连接成功，但配置未初始化")
            return True
    
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("智能交通流预测系统 - 数据库初始化")
    print("=" * 60)
    print()
    
    # 检查环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('MYSQL_USER'):
        print("⚠️  警告: 未找到.env文件或环境变量未设置")
        print("请创建.env文件并配置数据库信息")
        print("\n示例:")
        print("MYSQL_USER=root")
        print("MYSQL_PASSWORD=your_password")
        print("MYSQL_DATABASE=traffic_db")
        return
    
    # 步骤1: 创建数据库
    print("步骤 1/4: 创建数据库")
    print("-" * 60)
    if not create_database():
        print("\n❌ 数据库初始化失败")
        return
    
    # 步骤2: 创建表
    print("\n步骤 2/4: 创建数据库表")
    print("-" * 60)
    if not create_tables():
        print("\n❌ 数据库初始化失败")
        return
    
    # 步骤3: 初始化配置
    print("\n步骤 3/4: 初始化系统配置")
    print("-" * 60)
    if not initialize_config():
        print("\n⚠️  配置初始化失败，但数据库已创建")
    
    # 步骤4: 测试连接
    print("\n步骤 4/4: 测试数据库连接")
    print("-" * 60)
    test_connection()
    
    print("\n" + "=" * 60)
    print("✅ 数据库初始化完成！")
    print("=" * 60)
    print("\n💡 提示:")
    print("  - 数据库名称: traffic_db")
    print("  - 已创建5个表: predictions, training_records, api_logs, ")
    print("                 model_performance, system_config")
    print("  - 可以开始使用系统了！")
    print()


if __name__ == "__main__":
    main()

