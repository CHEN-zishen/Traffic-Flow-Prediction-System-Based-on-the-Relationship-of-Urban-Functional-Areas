"""从GitHub下载更多交通数据集"""
import os
import requests
from pathlib import Path
import zipfile
import numpy as np
from tqdm import tqdm

def download_file(url, save_path, description=""):
    """下载文件并显示进度条"""
    print(f"\n下载: {description}")
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
    """下载多个PeMS数据集"""
    
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 70)
    print("下载PeMS交通数据集")
    print("=" * 70)
    
    # 数据集配置
    datasets = {
        "PeMS03": {
            "url": "https://github.com/Davidham3/STSGCN/raw/master/data/PEMS03/PEMS03.npz",
            "description": "PeMS03 - 358个传感器, 26,208个时间步",
            "filename": "pems03.npz"
        },
        "PeMS04": {
            "url": "https://github.com/Davidham3/STSGCN/raw/master/data/PEMS04/PEMS04.npz",
            "description": "PeMS04 - 307个传感器, 16,992个时间步 (已有)",
            "filename": "pems04.npz"
        },
        "PeMS07": {
            "url": "https://github.com/Davidham3/STSGCN/raw/master/data/PEMS07/PEMS07.npz",
            "description": "PeMS07 - 883个传感器, 28,224个时间步",
            "filename": "pems07.npz"
        },
        "PeMS08": {
            "url": "https://github.com/Davidham3/STSGCN/raw/master/data/PEMS08/PEMS08.npz",
            "description": "PeMS08 - 170个传感器, 17,856个时间步",
            "filename": "pems08.npz"
        }
    }
    
    print("\n可用数据集:")
    for i, (name, info) in enumerate(datasets.items(), 1):
        print(f"{i}. {name}: {info['description']}")
    
    print("\n" + "=" * 70)
    
    # 下载所有数据集
    downloaded = []
    failed = []
    
    for name, info in datasets.items():
        save_path = data_dir / info['filename']
        
        # 检查是否已存在
        if save_path.exists():
            print(f"\n[跳过] {name} - 文件已存在")
            downloaded.append(name)
            continue
        
        # 下载
        if download_file(info['url'], save_path, f"{name} - {info['description']}"):
            
            # 验证文件
            try:
                data = np.load(save_path)
                print(f"  数据形状: {data['data'].shape}")
                downloaded.append(name)
            except Exception as e:
                print(f"  [ERROR] 文件验证失败: {e}")
                failed.append(name)
                save_path.unlink()  # 删除损坏的文件
        else:
            failed.append(name)
    
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
    
    print("\n" + "=" * 70)
    print("数据集信息:")
    print("=" * 70)
    
    # 显示已下载数据集的详细信息
    for name, info in datasets.items():
        save_path = data_dir / info['filename']
        if save_path.exists():
            try:
                data = np.load(save_path)
                shape = data['data'].shape
                print(f"\n{name} ({info['filename']}):")
                print(f"  形状: {shape}")
                print(f"  时间步: {shape[0]}")
                print(f"  传感器: {shape[1]}")
                print(f"  特征数: {shape[2]}")
                print(f"  文件大小: {save_path.stat().st_size / 1024 / 1024:.2f} MB")
            except Exception as e:
                print(f"\n{name}: 读取失败 - {e}")

def download_additional_datasets():
    """下载其他GitHub上的交通数据集"""
    
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 70)
    print("下载额外的交通数据集")
    print("=" * 70)
    
    # 其他数据集
    additional = {
        "METR-LA": {
            "url": "https://github.com/liyaguang/DCRNN/raw/master/data/metr-la.h5",
            "description": "洛杉矶高速公路交通数据",
            "filename": "metr_la.h5"
        },
        "PEMS-BAY": {
            "url": "https://github.com/liyaguang/DCRNN/raw/master/data/pems-bay.h5",
            "description": "旧金山湾区交通数据",
            "filename": "pems_bay.h5"
        }
    }
    
    for name, info in additional.items():
        save_path = data_dir / info['filename']
        
        if save_path.exists():
            print(f"\n[跳过] {name} - 文件已存在")
            continue
        
        download_file(info['url'], save_path, f"{name} - {info['description']}")

if __name__ == "__main__":
    print("=" * 70)
    print("交通数据集下载工具")
    print("=" * 70)
    
    # 检查网络连接
    try:
        requests.get("https://github.com", timeout=5)
        print("[OK] 网络连接正常")
    except:
        print("[ERROR] 无法连接到GitHub，请检查网络")
        exit(1)
    
    # 下载PeMS系列数据集
    download_pems_datasets()
    
    # 询问是否下载额外数据集
    print("\n" + "=" * 70)
    response = input("\n是否下载额外的交通数据集 (METR-LA, PEMS-BAY)? [y/N]: ")
    if response.lower() in ['y', 'yes']:
        download_additional_datasets()
    
    print("\n" + "=" * 70)
    print("所有下载任务完成！")
    print("=" * 70)
    print("\n数据保存位置: data/raw/")
    print("\n使用方法:")
    print("1. 这些数据集可以用于训练更强大的模型")
    print("2. 更多的数据可以提高预测准确性")
    print("3. 不同地区的数据可以测试模型泛化能力")
    print("=" * 70)

