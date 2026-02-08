"""测试密码验证"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.utils.auth import hash_password, verify_password

# 测试密码加密和验证
password = "admin123"

print("=" * 60)
print("密码验证测试")
print("=" * 60)
print()

# 生成新的密码哈希
print(f"原始密码: {password}")
new_hash = hash_password(password)
print(f"新生成的哈希: {new_hash}")
print()

# 测试验证
result = verify_password(password, new_hash)
print(f"验证新哈希: {'成功' if result else '失败'}")
print()

# 测试SQL中的哈希
sql_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIE.yI5k5W"
print(f"SQL中的哈希: {sql_hash}")
result = verify_password(password, sql_hash)
print(f"验证SQL哈希: {'成功' if result else '失败'}")
print()

# 测试错误密码
result = verify_password("wrong_password", sql_hash)
print(f"验证错误密码: {'成功' if result else '失败(预期)'}")
print()

print("=" * 60)
print("请将下面的哈希用于更新数据库:")
print("=" * 60)
print(new_hash)
print()
print("SQL更新语句:")
print(f"UPDATE users SET password_hash = '{new_hash}' WHERE username = 'admin';")

