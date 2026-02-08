"""从最新可用源下载PeMS交通数据集"""
import os
import requests
from pathlib import Path
import numpy as np
from tqdm import tqdm
def download_file(url, save_path, description=""):
    """下载文件并显示进度条"""
    print(f"\n[下载] {description}")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(save_path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
                print(f"[OK] 下载完成")
            else:
                with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        size = f.write(chunk)
                        pbar.update(size)
        
        return True
    except Exception as e:
        print(f"[ERROR] 下载失败: {e}")
        return False

def download_pems_datasets():
    """下载PeMS数据集（使用最新可用源）"""
    
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("PeMS交通数据集下载工具")
    print("=" * 70)
    
    # 更新的数据集配置（使用可用的源）
    datasets = [
        {
            "name": "PeMS03",
            "filename": "pems03.npz",
            "description": "358个传感器, 26,208个时间步",
            "urls": [
                "https://github.com/guoshnBJTU/ASTGNN/raw/main/data/PEMS03/PEMS03.npz",
                "https://raw.githubusercontent.com/nnzhan/Graph-WaveNet/master/data/PEMS03/PEMS03.npz"
            ]
        },
        {
            "name": "PeMS04",
            "filename": "pems04.npz",
            "description": "307个传感器, 16,992个时间步",
            "urls": [
                "https://github.com/guoshnBJTU/ASTGNN/raw/main/data/PEMS04/PEMS04.npz",
                "https://raw.githubusercontent.com/nnzhan/Graph-WaveNet/master/data/PEMS04/PEMS04.npz"
            ]
        },
        {
            "name": "PeMS07",
            "filename": "pems07.npz",
            "description": "883个传感器, 28,224个时间步",
            "urls": [
                "https://github.com/guoshnBJTU/ASTGNN/raw/main/data/PEMS07/PEMS07.npz",
                "https://raw.githubusercontent.com/nnzhan/Graph-WaveNet/master/data/PEMS07/PEMS07.npz"
            ]
        },
        {
            "name": "PeMS08",
            "filename": "pems08.npz",
            "description": "170个传感器, 17,856个时间步",
            "urls": [
                "https://github.com/guoshnBJTU/ASTGNN/raw/main/data/PEMS08/PEMS08.npz",
                "https://raw.githubusercontent.com/nnzhan/Graph-WaveNet/master/data/PEMS08/PEMS08.npz"
            ]
        }
    ]
    
    print("\n可用数据集:")
    for i, ds in enumerate(datasets, 1):
        print(f"{i}. {ds['name']}: {ds['description']}")
    
    print("\n" + "=" * 70)
    
    # 下载数据集
    downloaded = []
    failed = []
    
    for ds in datasets:
        save_path = data_dir / ds['filename']
        
        # 检查是否已存在
        if save_path.exists():
            print(f"\n[跳过] {ds['name']} - 文件已存在")
            downloaded.append(ds['name'])
            continue
        
        # 尝试多个URL
        success = False
        for url in ds['urls']:
            print(f"\n[尝试] {ds['name']} - {ds['description']}")
            print(f"URL: {url}")
            
            if download_file(url, save_path, ds['name']):
                # 验证文件
                try:
                    data = np.load(save_path)
                    print(f"  [OK] 数据形状: {data['data'].shape}")
                    downloaded.append(ds['name'])
                    success = True
                    break
                except Exception as e:
                    print(f"  [ERROR] 文件验证失败: {e}")
                    save_path.unlink()  # 删除损坏的文件
        
        if not success:
            failed.append(ds['name'])
    
    # 总结
    print("\n" + "=" * 70)
    print("下载完成")
    print("=" * 70)
    
    if downloaded:
        print(f"\n[OK] 成功: {len(downloaded)}个数据集")
        for name in downloaded:
            print(f"  - {name}")
    
    if failed:
        print(f"\n[ERROR] 失败: {len(failed)}个数据集")
        for name in failed:
            print(f"  - {name}")
    
    # 显示数据集信息
    print("\n" + "=" * 70)
    print("数据集详情:")
    print("=" * 70)
    
    for ds in datasets:
        save_path = data_dir / ds['filename']
        if save_path.exists():
            try:
                data = np.load(save_path)
                shape = data['data'].shape
                size_mb = save_path.stat().st_size / 1024 / 1024
                
                print(f"\n{ds['name']} ({ds['filename']}):")
                print(f"  形状: {shape}")
                print(f"  时间步: {shape[0]}")
                print(f"  传感器: {shape[1]}")
                print(f"  特征数: {shape[2]}")
                print(f"  文件大小: {size_mb:.2f} MB")
            except Exception as e:
                print(f"\n{ds['name']}: 读取失败 - {e}")

def show_usage_guide():
    """显示使用指南"""
    print("\n" + "=" * 70)
    print("使用指南")
    print("=" * 70)
    print("\n1. 切换数据集:")
    print("   编辑 configs/data_config.yaml")
    print("   修改 dataset.path 为新数据集路径")
    print("\n2. 重新训练模型:")
    print("   python src/scripts/train_model.py")
    print("\n3. 使用新数据预测:")
    print("   自动使用配置文件中指定的数据集")
    print("\n4. 数据集对比:")
    print("   - PeMS03: 中等规模，适合一般实验")
    print("   - PeMS04: 当前使用，平衡性能和速度")
    print("   - PeMS07: 大规模，最多传感器，训练时间长")
    print("   - PeMS08: 小规模，快速实验")
    print("=" * 70)

if __name__ == "__main__":
    print("=" * 70)
    print("PeMS交通数据集下载工具")
    print("=" * 70)
    
    # 检查网络连接
    try:
        requests.get("https://github.com", timeout=5)
        print("[OK] 网络连接正常")
    except:
        print("[WARNING] 无法连接到GitHub，可能影响下载")
    
    # 下载数据集
    download_pems_datasets()
    
    # 显示使用指南
    show_usage_guide()
    
    print("\n" + "=" * 70)
    print("完成！数据保存在: data/raw/")
    print("=" * 70)

