"""测试拥堵状态判断逻辑"""
import requests

API_BASE = "http://127.0.0.1:8000"

print("=" * 70)
print("测试拥堵状态判断")
print("=" * 70)

# 执行10次预测，查看拥堵状态分布
congestion_counts = {}

for i in range(10):
    print(f"\n[{i+1}/10] 预测中...")
    
    try:
        response = requests.get(f"{API_BASE}/predict/demo", params={"model_type": "lstm"})
        if response.status_code == 200:
            data = response.json()
            
            sensor_id = data.get('sensor_id')
            flow = data.get('flow_prediction')
            density = data.get('density_prediction')
            congestion = data.get('congestion_level')
            
            print(f"  传感器: {sensor_id}")
            print(f"  流量: {flow:.2f}")
            print(f"  密度: {density:.3f}")
            print(f"  拥堵状态: {congestion}")
            
            # 统计拥堵状态
            congestion_counts[congestion] = congestion_counts.get(congestion, 0) + 1
            
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "=" * 70)
print("拥堵状态统计:")
print("=" * 70)
for status, count in congestion_counts.items():
    print(f"  {status}: {count}次")

print("\n" + "=" * 70)
print("分析:")
print("=" * 70)
if len(congestion_counts) == 1 and '严重拥堵' in congestion_counts:
    print("⚠️  所有预测都是'严重拥堵'")
    print("问题: 拥堵状态判断逻辑可能有问题")
    print("\n可能原因:")
    print("1. 密度预测值总是很高（>0.7）")
    print("2. 判断阈值设置不合理")
    print("3. 模型输出的density值范围不正确")
elif len(congestion_counts) >= 3:
    print("✅ 拥堵状态分布正常，有多种状态")
else:
    print("⚠️  拥堵状态种类较少")

print("=" * 70)

