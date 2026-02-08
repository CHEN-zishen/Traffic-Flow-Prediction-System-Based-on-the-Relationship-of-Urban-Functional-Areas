"""完整诊断脚本 - 检查为什么数据不显示"""
import requests
import pymysql
import json

print("=" * 70)
print("诊断：预测次数不显示问题")
print("=" * 70)

# 1. 检查API是否运行
print("\n[步骤1] 检查API服务")
print("-" * 70)
try:
    response = requests.get("http://127.0.0.1:8000/health", timeout=3)
    if response.status_code == 200:
        print("[OK] API服务正在运行")
        data = response.json()
        print(f"   模型加载状态: {data.get('model_loaded')}")
    else:
        print("[ERROR] API服务响应异常")
except Exception as e:
    print(f"[ERROR] API服务未运行或无法连接: {e}")
    print("   请先启动API: python run_api.py")
    exit(1)

# 2. 检查数据库连接
print("\n[步骤2] 检查数据库连接")
print("-" * 70)
try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='traffic_db',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    print("[OK] 数据库连接成功")
    
    # 检查表结构
    cursor.execute("DESCRIBE predictions")
    columns = cursor.fetchall()
    
    # 检查关键字段
    congestion_field = None
    sensor_id_field = None
    for col in columns:
        if col[0] == 'congestion_prediction':
            congestion_field = col
        if col[0] == 'sensor_id':
            sensor_id_field = col
    
    print(f"\n   sensor_id 字段类型: {sensor_id_field[1] if sensor_id_field else '未找到'}")
    print(f"   congestion_prediction 类型: {congestion_field[1] if congestion_field else '未找到'}")
    
    # 检查枚举值
    if congestion_field and 'enum' in congestion_field[1].lower():
        if "'正常'" in congestion_field[1] and "'严重拥堵'" in congestion_field[1]:
            print("   [OK] 枚举值包含: 畅通, 正常, 拥堵, 严重拥堵")
        else:
            print(f"   [ERROR] 枚举值错误: {congestion_field[1]}")
            print("   需要运行: quick_fix.sql")
    
    # 检查现有数据
    cursor.execute("SELECT COUNT(*) FROM predictions")
    count = cursor.fetchone()[0]
    print(f"\n   数据库中的记录数: {count}")
    
    if count > 0:
        cursor.execute("SELECT sensor_id, flow_prediction, congestion_prediction, created_at FROM predictions ORDER BY created_at DESC LIMIT 3")
        records = cursor.fetchall()
        print("\n   最近的记录:")
        for i, record in enumerate(records, 1):
            print(f"   {i}. sensor_id={record[0]}, flow={record[1]:.2f}, congestion={record[2]}, time={record[3]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"[ERROR] 数据库连接失败: {e}")
    print("   请检查MySQL服务是否运行")
    exit(1)

# 3. 测试预测API
print("\n[步骤3] 测试预测功能")
print("-" * 70)
try:
    print("正在调用预测API...")
    response = requests.get(
        "http://127.0.0.1:8000/predict/demo",
        params={"sensor_id": "sensor_test", "model_type": "lstm"},
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("[OK] 预测成功")
        print(f"   sensor_id: {data.get('sensor_id')}")
        print(f"   flow_prediction: {data.get('flow_prediction'):.2f}")
        print(f"   congestion_level: {data.get('congestion_level')}")
        
        # 立即检查数据库
        print("\n   检查数据库是否保存...")
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='traffic_db',
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM predictions")
        new_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        if new_count > count:
            print(f"   [OK] 数据已保存! 记录数: {count} -> {new_count}")
        else:
            print(f"   [ERROR] 数据未保存! 记录数仍然是: {new_count}")
            print("   请检查API终端是否有错误信息")
    else:
        print(f"[ERROR] 预测失败: {response.status_code}")
        print(f"   错误: {response.text}")
except Exception as e:
    print(f"[ERROR] 预测请求失败: {e}")

# 4. 检查统计API
print("\n[步骤4] 检查统计API")
print("-" * 70)
try:
    response = requests.get("http://127.0.0.1:8000/stats/summary", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] 统计API返回:")
        print(f"   总预测次数: {data.get('total_predictions')}")
        print(f"   总训练次数: {data.get('total_training_runs')}")
        print(f"   拥堵分布: {data.get('congestion_distribution')}")
        
        if data.get('total_predictions') == 0:
            print("\n   [WARNING] 总预测次数为0，但数据库可能有数据")
            print("   可能的原因:")
            print("   1. API服务未重启（旧代码仍在运行）")
            print("   2. 数据库查询逻辑有问题")
    else:
        print(f"[ERROR] 统计API失败: {response.status_code}")
except Exception as e:
    print(f"[ERROR] 统计请求失败: {e}")

# 5. 检查历史记录API
print("\n[步骤5] 检查历史记录API")
print("-" * 70)
try:
    response = requests.get("http://127.0.0.1:8000/history/recent?limit=5", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] 历史记录API返回:")
        print(f"   记录数量: {data.get('count')}")
        
        if data.get('count') == 0:
            print("   [WARNING] API返回0条记录")
            print("   但数据库中可能有数据 - 这说明API查询有问题")
        else:
            records = data.get('records', [])[:3]
            print(f"\n   最近的记录:")
            for i, record in enumerate(records, 1):
                print(f"   {i}. sensor_id={record.get('sensor_id')}, flow={record.get('flow_prediction'):.2f}")
    else:
        print(f"[ERROR] 历史记录API失败: {response.status_code}")
except Exception as e:
    print(f"[ERROR] 历史记录请求失败: {e}")

# 总结
print("\n" + "=" * 70)
print("诊断总结")
print("=" * 70)

print("\n请检查以下内容:")
print("1. [?] 是否运行了 quick_fix.sql 修复数据库表？")
print("2. [?] 是否重启了API服务（Ctrl+C 然后 python run_api.py）？")
print("3. [?] API终端是否显示 '[DB] 预测结果已保存到数据库' ？")
print("4. [?] 是否刷新了浏览器（Ctrl+F5）？")

print("\n如果以上都做了但仍然不显示，请发送以下信息给我：")
print("- API终端的最新输出（最后20行）")
print("- 这个诊断脚本的完整输出")
print("=" * 70)

