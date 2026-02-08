"""批量预测 - 使用多个不同传感器"""
import requests
import time

API_BASE = "http://127.0.0.1:8000"

print("=" * 70)
print("批量预测 - 使用多个传感器")
print("=" * 70)

# 预测20次，使用不同的传感器
num_predictions = 20

for i in range(num_predictions):
    print(f"\n[{i+1}/{num_predictions}] 正在预测...")
    
    try:
        # 调用预测API（不指定sensor_id，让系统随机选择）
        response = requests.get(
            f"{API_BASE}/predict/demo",
            params={"model_type": "lstm"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  传感器: {data.get('sensor_id')} (索引: {data.get('sensor_index')})")
            print(f"  流量: {data.get('flow_prediction'):.2f}")
            print(f"  拥堵: {data.get('congestion_level')}")
            print(f"  置信度: {data.get('confidence')*100:.1f}%")
        else:
            print(f"  失败: {response.status_code}")
            
    except Exception as e:
        print(f"  错误: {e}")
    
    # 稍微等待一下，避免请求太快
    if i < num_predictions - 1:
        time.sleep(0.5)

print("\n" + "=" * 70)
print("批量预测完成！")
print("=" * 70)
print("\n请刷新浏览器查看数据概览页面：")
print("- 总预测次数应该增加了20")
print("- 流量趋势图应该显示曲线")
print("- 拥堵分布图应该显示不同颜色")
print("=" * 70)

