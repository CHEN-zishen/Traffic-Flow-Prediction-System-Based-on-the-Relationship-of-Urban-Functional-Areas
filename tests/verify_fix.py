"""验证拥堵判断修复效果"""
import requests
import time

API_BASE = "http://127.0.0.1:8000"

print("=" * 70)
print("验证拥堵状态判断修复")
print("=" * 70)

# 执行20次预测，统计拥堵状态分布
congestion_counts = {}
density_values = []

for i in range(20):
    print(f"\r[{i+1}/20] 预测中...", end='', flush=True)
    
    try:
        response = requests.get(f"{API_BASE}/predict/demo", params={"model_type": "lstm"})
        if response.status_code == 200:
            data = response.json()
            
            density = data.get('density_prediction')
            congestion = data.get('congestion_level')
            
            # 统计
            congestion_counts[congestion] = congestion_counts.get(congestion, 0) + 1
            density_values.append(density)
            
        time.sleep(0.3)
            
    except Exception as e:
        print(f"\n  错误: {e}")

print("\n")
print("=" * 70)
print("拥堵状态分布:")
print("=" * 70)

for status in ['畅通', '正常', '拥堵', '严重拥堵']:
    count = congestion_counts.get(status, 0)
    percentage = (count / 20) * 100
    bar = '█' * int(percentage / 5)
    print(f"{status:8s}: {count:2d}次 ({percentage:5.1f}%) {bar}")

print("\n" + "=" * 70)
print("密度值统计:")
print("=" * 70)
if density_values:
    print(f"最小值: {min(density_values):.3f}")
    print(f"最大值: {max(density_values):.3f}")
    print(f"平均值: {sum(density_values)/len(density_values):.3f}")

print("\n" + "=" * 70)
print("验证结果:")
print("=" * 70)

unique_states = len(congestion_counts)
if unique_states >= 3:
    print("[OK] 拥堵状态分布正常！")
    print(f"     出现了 {unique_states} 种不同的拥堵状态")
    print("\n建议:")
    print("- 刷新浏览器查看数据概览页面")
    print("- 拥堵分布饼图应该显示多种颜色")
elif unique_states >= 2:
    print("[提示] 拥堵状态有所改善")
    print(f"      出现了 {unique_states} 种状态")
    print("      可能需要更多预测数据")
else:
    print("[WARNING] 拥堵状态仍然单一")
    print("         可能需要进一步调整阈值")

print("=" * 70)

