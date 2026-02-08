"""检查数据库表的枚举值定义"""
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='traffic_db',
    charset='utf8mb4'
)
cursor = conn.cursor()

print("=" * 70)
print("检查数据库表结构")
print("=" * 70)

# 检查表结构
cursor.execute("SHOW CREATE TABLE predictions")
result = cursor.fetchone()

print("\n完整的CREATE TABLE语句:")
print(result[1])

# 检查具体的枚举列
cursor.execute("SHOW COLUMNS FROM predictions LIKE 'congestion_prediction'")
result = cursor.fetchone()

print("\n" + "=" * 70)
print("congestion_prediction 字段详情:")
print("=" * 70)
print(f"Field: {result[0]}")
print(f"Type: {result[1]}")
print(f"Null: {result[2]}")
print(f"Key: {result[3]}")
print(f"Default: {result[4]}")
print(f"Extra: {result[5]}")

# 检查是否包含所有需要的枚举值
enum_type = result[1]
if "'正常'" in enum_type and "'严重拥堵'" in enum_type:
    print("\n✅ 枚举值正确包含: 畅通, 正常, 拥堵, 严重拥堵")
else:
    print(f"\n❌ 枚举值错误！")
    print(f"当前枚举值: {enum_type}")
    print("\n需要运行 quick_fix.sql 修复！")

cursor.close()
conn.close()

print("=" * 70)

