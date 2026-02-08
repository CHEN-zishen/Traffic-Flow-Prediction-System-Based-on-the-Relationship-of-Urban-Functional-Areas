"""快速检查API状态"""
import requests

print("检查API服务状态...")

# 1. 检查统计数据
try:
    response = requests.get("http://127.0.0.1:8000/stats/summary")
    data = response.json()
    
    print(f"\nAPI返回的统计数据:")
    print(f"  总预测次数: {data.get('total_predictions')}")
    print(f"  拥堵分布: {data.get('congestion_distribution')}")
    
    if data.get('total_predictions') == 0:
        print("\n[问题] API返回预测次数为0")
        print("这说明API服务使用的是旧代码，没有正确重启！")
        print("\n请确认:")
        print("1. 是否在运行API的终端按了 Ctrl+C 停止？")
        print("2. 是否重新运行了 python run_api.py ？")
        print("3. 终端是否显示了启动信息？")
    else:
        print(f"\n[OK] API正常，返回了 {data.get('total_predictions')} 条记录")
        
except Exception as e:
    print(f"\n[错误] 无法连接到API: {e}")
    print("请确认API服务是否在运行")

# 2. 检查历史记录
try:
    response = requests.get("http://127.0.0.1:8000/history/recent?limit=5")
    data = response.json()
    
    print(f"\nAPI返回的历史记录:")
    print(f"  记录数量: {data.get('count')}")
    
    if data.get('count') == 0:
        print("\n[问题] API查询返回0条记录，但数据库有18条")
        print("这确认了API服务没有重启！")
except Exception as e:
    print(f"\n[错误] 无法获取历史记录: {e}")

print("\n" + "="*60)
print("解决方法:")
print("="*60)
print("1. 找到运行 'python run_api.py' 的终端窗口")
print("2. 在那个终端按 Ctrl+C（会看到 ^C 和停止信息）")
print("3. 等待完全停止后，重新运行: python run_api.py")
print("4. 看到 'Uvicorn running on...' 后")
print("5. 回到浏览器，按 Ctrl+Shift+R 强制刷新")
print("="*60)

