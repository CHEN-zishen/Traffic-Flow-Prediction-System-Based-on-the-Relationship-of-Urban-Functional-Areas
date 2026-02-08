"""检查图表数据"""
import requests
import pymysql

print("=" * 70)
print("检查图表为什么没有数据")
print("=" * 70)

# 1. 检查API统计数据
print("\n[1] 检查统计API返回")
print("-" * 70)
response = requests.get("http://127.0.0.1:8000/stats/summary")
data = response.json()
print(f"总预测次数: {data.get('total_predictions')}")
print(f"拥堵分布: {data.get('congestion_distribution')}")

if all(v == 0 for v in data.get('congestion_distribution', {}).values()):
    print("\n[问题] 拥堵分布全是0！")

# 2. 检查历史记录API
print("\n[2] 检查历史记录API返回")
print("-" * 70)
response = requests.get("http://127.0.0.1:8000/history/recent?limit=10")
data = response.json()
print(f"记录数量: {data.get('count')}")

if data.get('count') == 0:
    print("\n[问题] 历史记录返回0条！")
else:
    records = data.get('records', [])
    if records:
        print(f"\n最近的记录:")
        for i, r in enumerate(records[:3], 1):
            print(f"  {i}. sensor_id={r.get('sensor_id')}, flow={r.get('flow_prediction')}, congestion={r.get('congestion_prediction')}")

# 3. 直接查询数据库
print("\n[3] 直接查询数据库")
print("-" * 70)
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='123456',
    database='traffic_db',
    charset='utf8mb4'
)
cursor = conn.cursor()

# 查询总数
cursor.execute("SELECT COUNT(*) FROM predictions")
total = cursor.fetchone()[0]
print(f"数据库总记录数: {total}")

# 查询最近的记录
cursor.execute("""
    SELECT sensor_id, flow_prediction, congestion_prediction, created_at 
    FROM predictions 
    ORDER BY created_at DESC 
    LIMIT 5
""")
records = cursor.fetchall()
print(f"\n数据库中最近的5条记录:")
for i, r in enumerate(records, 1):
    print(f"  {i}. sensor_id={r[0]}, flow={r[1]:.2f}, congestion={r[2]}, time={r[3]}")

# 查询拥堵分布
cursor.execute("""
    SELECT congestion_prediction, COUNT(*) as count 
    FROM predictions 
    WHERE congestion_prediction IS NOT NULL
    GROUP BY congestion_prediction
""")
congestion_stats = cursor.fetchall()
print(f"\n数据库中的拥堵分布:")
for row in congestion_stats:
    print(f"  {row[0]}: {row[1]}条")

cursor.close()
conn.close()

# 总结
print("\n" + "=" * 70)
print("诊断结果")
print("=" * 70)

if total > 0 and data.get('count', 0) == 0:
    print("\n[问题确认] 数据库有数据，但API查询返回空！")
    print("可能原因:")
    print("1. ORM模型的to_dict()方法有问题")
    print("2. 数据类型转换失败")
    print("3. SQLAlchemy查询失败但没有报错")
    print("\n解决方法: 需要检查src/utils/db_utils.py中的查询逻辑")
elif total == 0:
    print("\n[问题确认] 数据库没有数据！")
    print("说明预测虽然成功，但没有保存到数据库")
else:
    print("\n[正常] 数据库有数据，API也能查询到")

print("=" * 70)

