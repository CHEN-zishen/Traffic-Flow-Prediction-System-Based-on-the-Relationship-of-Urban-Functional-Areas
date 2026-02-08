"""
认证系统初始化脚本
运行此脚本以设置用户认证系统
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.db_utils import get_engine, get_session, DatabaseManager
from src.models_db.user import User
from src.utils.auth import hash_password
from sqlalchemy import text
import pymysql


def init_auth_system():
    """初始化认证系统"""
    print("=" * 60)
    print("🔐 认证系统初始化")
    print("=" * 60)
    print()
    
    # 初始化数据库连接
    print("📝 初始化数据库连接...")
    try:
        db_manager = DatabaseManager()
        print("✅ 数据库连接成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    
    # 步骤1: 创建users表
    print("\n📝 步骤1: 创建users表...")
    try:
        engine = get_engine()
        
        # 读取SQL文件
        sql_file = project_root / "database" / "users_table.sql"
        if not sql_file.exists():
            print("❌ 错误: 找不到 database/users_table.sql")
            return False
        
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 执行SQL（分割多个语句）
        with engine.connect() as conn:
            # 分割SQL语句（以分号分隔）
            statements = [s.strip() for s in sql_content.split(';') if s.strip()]
            
            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        # 忽略"表已存在"错误
                        if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                            print(f"⚠️  警告: {e}")
        
        print("✅ users表创建成功")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    # 步骤2: 创建默认管理员账户
    print("\n📝 步骤2: 创建默认管理员账户...")
    try:
        session = get_session()
        
        # 检查admin用户是否已存在
        existing_admin = session.query(User).filter(User.username == 'admin').first()
        
        if existing_admin:
            print("ℹ️  管理员账户已存在，跳过创建")
        else:
            # 创建管理员账户
            admin_user = User(
                username='admin',
                email='admin@traffic.com',
                password_hash=hash_password('admin123'),
                nickname='系统管理员',
                role='admin',
                status=1
            )
            
            session.add(admin_user)
            session.commit()
            print("✅ 管理员账户创建成功")
            print("\n📋 管理员登录信息:")
            print("   用户名: admin")
            print("   密码:   admin123")
            print("   ⚠️  请在首次登录后修改密码！")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    # 步骤3: 验证安装
    print("\n📝 步骤3: 验证安装...")
    try:
        session = get_session()
        user_count = session.query(User).count()
        print(f"✅ 当前用户数: {user_count}")
        session.close()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    # 完成
    print("\n" + "=" * 60)
    print("✅ 认证系统初始化完成！")
    print("=" * 60)
    print("\n🚀 下一步:")
    print("   1. 启动API服务: python run_api.py")
    print("   2. 启动Web服务: python run_web_admin.py")
    print("   3. 访问登录页面: http://127.0.0.1:5000/login")
    print("\n📖 详细文档:")
    print("   - 快速开始: docs/AUTH_QUICKSTART.md")
    print("   - 完整文档: docs/AUTH_SYSTEM.md")
    print()
    
    return True


if __name__ == '__main__':
    try:
        success = init_auth_system()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  安装已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

