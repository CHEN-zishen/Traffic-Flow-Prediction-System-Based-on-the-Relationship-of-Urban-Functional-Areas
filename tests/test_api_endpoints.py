"""详细测试所有API端点"""
import requests
import json

API_BASE = "http://127.0.0.1:8000"

print("=" * 70)
print("测试所有API端点")
print("=" * 70)

# 1. 测试统计摘要
print("\n[1] 测试 /stats/summary")
print("-" * 70)
try:
    response = requests.get(f"{API_BASE}/stats/summary")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("返回的JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")

# 2. 测试历史记录
print("\n[2] 测试 /history/recent?limit=10")
print("-" * 70)
try:
    response = requests.get(f"{API_BASE}/history/recent", params={"limit": 10})
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"记录数量: {data.get('count')}")
        
        records = data.get('records', [])
        if records:
            print("\n前3条记录的完整JSON:")
            for i, record in enumerate(records[:3], 1):
                print(f"\n记录 {i}:")
                print(json.dumps(record, indent=2, ensure_ascii=False))
        else:
            print("没有记录！")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")

print("\n" + "=" * 70)

