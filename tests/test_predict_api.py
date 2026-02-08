"""测试预测API接口"""
import requests
import json

API_URL = "http://127.0.0.1:8000/predict/demo"

print("=" * 60)
print("测试预测API接口")
print("=" * 60)

# 测试参数
params = {
    "sensor_id": "sensor_001",
    "model_type": "lstm"
}

print(f"\n请求URL: {API_URL}")
print(f"参数: {params}")
print("\n发送请求...")

try:
    response = requests.get(API_URL, params=params, timeout=30)
    
    print(f"\n状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("\n✅ 预测成功！")
        data = response.json()
        print(f"\n预测结果:")
        print(f"  - 传感器ID: {data.get('sensor_id')}")
        print(f"  - 流量预测: {data.get('flow_prediction'):.2f} 辆/5分钟")
        print(f"  - 密度预测: {data.get('density_prediction'):.3f}")
        print(f"  - 拥堵状态: {data.get('congestion_level')}")
        print(f"  - 置信度: {data.get('confidence') * 100:.1f}%")
        print(f"  - 模型类型: {data.get('model_type')}")
        print(f"\n输入数据（前3个时间步）:")
        input_data = data.get('input_data', [])[:3]
        for i, row in enumerate(input_data):
            print(f"  T-{i+1}: 流量={row[0]:.2f}, 速度={row[1]:.2f}, 占有率={row[2]:.3f}")
    else:
        print(f"\n❌ 请求失败！")
        print(f"\n错误详情:")
        try:
            error_data = response.json()
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
except requests.exceptions.ConnectionError:
    print("\n❌ 连接失败！")
    print("\n可能的原因:")
    print("  1. API服务未启动")
    print("  2. API服务端口不是8000")
    print("\n解决方法:")
    print("  请运行: python run_api.py")
    
except requests.exceptions.Timeout:
    print("\n❌ 请求超时！")
    print("\n可能的原因:")
    print("  1. 模型加载时间过长")
    print("  2. 服务器响应慢")
    
except Exception as e:
    print(f"\n❌ 未知错误: {e}")

print("\n" + "=" * 60)

