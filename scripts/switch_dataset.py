"""快速切换数据集工具"""
import yaml
from pathlib import Path
import numpy as np

def show_available_datasets():
    """显示可用的数据集"""
    data_dir = Path("data/raw")
    
    datasets = {
        "PeMS03": {"file": "pems03.npz", "sensors": 358, "timesteps": 26208, "features": 1},
        "PeMS04": {"file": "pems04.npz", "sensors": 307, "timesteps": 16992, "features": 3},
        "PeMS07": {"file": "pems07.npz", "sensors": 883, "timesteps": 28224, "features": 1},
        "PeMS08": {"file": "pems08.npz", "sensors": 170, "timesteps": 17856, "features": 3}
    }
    
    print("=" * 70)
    print("可用数据集")
    print("=" * 70)
    
    for i, (name, info) in enumerate(datasets.items(), 1):
        file_path = data_dir / info['file']
        status = "[OK]" if file_path.exists() else "[缺失]"
        features_desc = "流量+速度+占有率" if info['features'] == 3 else "仅流量"
        
        print(f"\n{i}. {name} {status}")
        print(f"   文件: {info['file']}")
        print(f"   传感器: {info['sensors']}")
        print(f"   时间步: {info['timesteps']}")
        print(f"   特征: {features_desc}")
        
        if file_path.exists():
            size_mb = file_path.stat().st_size / 1024 / 1024
            print(f"   大小: {size_mb:.2f} MB")
    
    return datasets

def get_current_dataset():
    """获取当前使用的数据集"""
    config_path = Path("configs/data_config.yaml")
    
    if not config_path.exists():
        return None
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    current_path = config.get('dataset', {}).get('path', '')
    
    # 从路径提取数据集名称
    if 'pems03' in current_path.lower():
        return 'PeMS03'
    elif 'pems04' in current_path.lower():
        return 'PeMS04'
    elif 'pems07' in current_path.lower():
        return 'PeMS07'
    elif 'pems08' in current_path.lower():
        return 'PeMS08'
    
    return None

def switch_dataset(dataset_name):
    """切换到指定数据集"""
    datasets = {
        "PeMS03": {"file": "pems03.npz", "sensors": 358, "timesteps": 26208},
        "PeMS04": {"file": "pems04.npz", "sensors": 307, "timesteps": 16992},
        "PeMS07": {"file": "pems07.npz", "sensors": 883, "timesteps": 28224},
        "PeMS08": {"file": "pems08.npz", "sensors": 170, "timesteps": 17856}
    }
    
    if dataset_name not in datasets:
        print(f"[ERROR] 数据集 '{dataset_name}' 不存在")
        return False
    
    info = datasets[dataset_name]
    data_path = Path("data/raw") / info['file']
    
    if not data_path.exists():
        print(f"[ERROR] 数据文件不存在: {data_path}")
        print("请先运行: python download_pems_datasets.py")
        return False
    
    # 读取配置
    config_path = Path("configs/data_config.yaml")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 更新配置
    config['dataset']['path'] = str(data_path)
    config['dataset']['num_sensors'] = info['sensors']
    config['dataset']['num_timesteps'] = info['timesteps']
    
    # 保存配置
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)
    
    print(f"\n[OK] 已切换到数据集: {dataset_name}")
    print(f"     文件: {info['file']}")
    print(f"     传感器: {info['sensors']}")
    print(f"     时间步: {info['timesteps']}")
    
    return True

def preview_dataset(dataset_name):
    """预览数据集"""
    datasets = {
        "PeMS03": "pems03.npz",
        "PeMS04": "pems04.npz",
        "PeMS07": "pems07.npz",
        "PeMS08": "pems08.npz"
    }
    
    if dataset_name not in datasets:
        print(f"[ERROR] 数据集 '{dataset_name}' 不存在")
        return
    
    data_path = Path("data/raw") / datasets[dataset_name]
    
    if not data_path.exists():
        print(f"[ERROR] 数据文件不存在: {data_path}")
        return
    
    try:
        data = np.load(data_path)
        traffic_data = data['data']
        
        print(f"\n{dataset_name} 数据预览")
        print("=" * 70)
        print(f"数据形状: {traffic_data.shape}")
        print(f"时间步数: {traffic_data.shape[0]}")
        print(f"传感器数: {traffic_data.shape[1]}")
        print(f"特征数: {traffic_data.shape[2]}")
        
        print(f"\n统计信息:")
        print(f"最小值: {traffic_data.min():.2f}")
        print(f"最大值: {traffic_data.max():.2f}")
        print(f"平均值: {traffic_data.mean():.2f}")
        print(f"标准差: {traffic_data.std():.2f}")
        
        print(f"\n前5个时间步，第1个传感器的数据:")
        print(traffic_data[:5, 0, :])
        
    except Exception as e:
        print(f"[ERROR] 读取数据失败: {e}")

if __name__ == "__main__":
    print("=" * 70)
    print("PeMS数据集切换工具")
    print("=" * 70)
    
    # 显示可用数据集
    datasets = show_available_datasets()
    
    # 显示当前使用的数据集
    current = get_current_dataset()
    if current:
        print(f"\n当前使用: {current}")
    
    # 交互式选择
    print("\n" + "=" * 70)
    print("请选择操作:")
    print("1. 切换数据集")
    print("2. 预览数据集")
    print("3. 退出")
    print("=" * 70)
    
    try:
        choice = input("\n请输入选项 (1-3): ").strip()
        
        if choice == '1':
            dataset_name = input("请输入数据集名称 (PeMS03/PeMS04/PeMS07/PeMS08): ").strip()
            if switch_dataset(dataset_name):
                print("\n[提示] 切换成功！请重新启动API和Web服务以使用新数据集")
        
        elif choice == '2':
            dataset_name = input("请输入数据集名称 (PeMS03/PeMS04/PeMS07/PeMS08): ").strip()
            preview_dataset(dataset_name)
        
        elif choice == '3':
            print("退出")
        
        else:
            print("[ERROR] 无效选项")
    
    except EOFError:
        print("\n[INFO] 在非交互式模式下运行")
        print("使用方法:")
        print("  python switch_dataset.py  # 交互式选择")
        print("  # 或在代码中导入使用:")
        print("  from switch_dataset import switch_dataset")
        print("  switch_dataset('PeMS07')")

