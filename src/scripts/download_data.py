"""
PeMS04数据集下载脚本
支持从GitHub和备用源下载数据
"""

import os
import sys
import requests
from pathlib import Path
from tqdm import tqdm
from typing import Optional
import hashlib

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import config


# 数据集URL配置
DATASET_URLS = {
    'flow': [
        'https://raw.githubusercontent.com/Davidham3/STSGCN/master/data/PeMS04/PeMS04_flow.csv',
        'https://github.com/Davidham3/ASTGCN/raw/master/data/PEMS04/pems04.npz',
    ],
    'backup': [
        'https://zenodo.org/record/5724362/files/PeMS04.zip',
    ]
}


class DataDownloader:
    """数据下载器"""
    
    def __init__(self, output_dir: str = None):
        """
        初始化下载器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir) if output_dir else Path(config.get('paths.data_raw'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 下载配置
        self.chunk_size = 8192
        self.timeout = 300
        self.retry_times = 3
    
    def download_file(
        self,
        url: str,
        filename: str,
        verify_md5: str = None,
        show_progress: bool = True
    ) -> bool:
        """
        下载单个文件
        
        Args:
            url: 下载URL
            filename: 保存文件名
            verify_md5: MD5校验码（可选）
            show_progress: 是否显示进度条
        
        Returns:
            是否下载成功
        """
        output_path = self.output_dir / filename
        
        # 检查文件是否已存在
        if output_path.exists():
            print(f"ℹ️  文件已存在: {filename}")
            if verify_md5:
                if self._verify_md5(output_path, verify_md5):
                    print(f"✅ MD5校验通过")
                    return True
                else:
                    print(f"⚠️  MD5校验失败，重新下载...")
                    output_path.unlink()
        
        # 尝试下载
        for attempt in range(1, self.retry_times + 1):
            try:
                print(f"📥 开始下载: {filename} (尝试 {attempt}/{self.retry_times})")
                print(f"🔗 URL: {url}")
                
                # 发送请求
                response = requests.get(
                    url,
                    stream=True,
                    timeout=self.timeout,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                response.raise_for_status()
                
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                
                # 下载文件
                with open(output_path, 'wb') as f:
                    if show_progress and total_size > 0:
                        # 使用进度条
                        with tqdm(
                            total=total_size,
                            unit='B',
                            unit_scale=True,
                            desc=filename
                        ) as pbar:
                            for chunk in response.iter_content(chunk_size=self.chunk_size):
                                if chunk:
                                    f.write(chunk)
                                    pbar.update(len(chunk))
                    else:
                        # 无进度条
                        for chunk in response.iter_content(chunk_size=self.chunk_size):
                            if chunk:
                                f.write(chunk)
                
                # 验证MD5
                if verify_md5:
                    if self._verify_md5(output_path, verify_md5):
                        print(f"✅ MD5校验通过")
                    else:
                        print(f"❌ MD5校验失败")
                        output_path.unlink()
                        return False
                
                print(f"✅ 下载成功: {filename}")
                return True
            
            except Exception as e:
                print(f"❌ 下载失败 (尝试 {attempt}/{self.retry_times}): {e}")
                if attempt < self.retry_times:
                    print(f"🔄 {2 ** attempt}秒后重试...")
                    import time
                    time.sleep(2 ** attempt)
                else:
                    print(f"❌ 下载失败，已达到最大重试次数")
                    return False
        
        return False
    
    def _verify_md5(self, filepath: Path, expected_md5: str) -> bool:
        """
        验证文件MD5
        
        Args:
            filepath: 文件路径
            expected_md5: 期望的MD5值
        
        Returns:
            是否匹配
        """
        md5_hash = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        
        actual_md5 = md5_hash.hexdigest()
        return actual_md5 == expected_md5
    
    def download_pems04_npz(self) -> bool:
        """
        下载PeMS04数据集（NPZ格式）
        
        Returns:
            是否下载成功
        """
        print("\n" + "=" * 60)
        print("下载 PeMS04 数据集（NPZ格式）")
        print("=" * 60)
        print()
        
        # 方案1: 从ASTGCN仓库下载NPZ文件（推荐）
        url = 'https://github.com/Davidham3/ASTGCN/raw/master/data/PEMS04/pems04.npz'
        filename = 'pems04.npz'
        
        success = self.download_file(url, filename)
        
        if success:
            print("\n✅ PeMS04数据集下载完成！")
            print(f"📁 保存位置: {self.output_dir / filename}")
            return True
        else:
            print("\n❌ 数据集下载失败")
            print("\n💡 备选方案:")
            print("  1. 手动下载: https://github.com/Davidham3/ASTGCN/tree/master/data/PEMS04")
            print(f"  2. 保存到: {self.output_dir}")
            print("  3. 文件名: pems04.npz")
            return False
    
    def download_sample_data(self) -> bool:
        """
        下载示例数据（用于测试）
        
        Returns:
            是否下载成功
        """
        print("\n" + "=" * 60)
        print("生成示例数据（用于测试）")
        print("=" * 60)
        print()
        
        try:
            import numpy as np
            
            # 生成模拟数据
            num_sensors = 307
            num_timesteps = 1000  # 缩小规模用于测试
            
            print("📊 生成模拟交通数据...")
            
            # 流量数据 (vehicles/hour)
            flow = np.random.uniform(50, 300, (num_timesteps, num_sensors))
            
            # 速度数据 (km/h)
            speed = np.random.uniform(30, 80, (num_timesteps, num_sensors))
            
            # 占有率数据 (0-1)
            occupancy = np.random.uniform(0.1, 0.8, (num_timesteps, num_sensors))
            
            # 保存为NPY文件
            np.save(self.output_dir / 'pems04_flow_sample.npy', flow)
            np.save(self.output_dir / 'pems04_speed_sample.npy', speed)
            np.save(self.output_dir / 'pems04_occupancy_sample.npy', occupancy)
            
            print(f"✅ 示例数据生成成功")
            print(f"📁 保存位置: {self.output_dir}")
            print(f"   - pems04_flow_sample.npy ({flow.shape})")
            print(f"   - pems04_speed_sample.npy ({speed.shape})")
            print(f"   - pems04_occupancy_sample.npy ({occupancy.shape})")
            
            return True
        
        except Exception as e:
            print(f"❌ 示例数据生成失败: {e}")
            return False
    
    def check_data_files(self) -> bool:
        """
        检查数据文件是否存在
        
        Returns:
            数据是否就绪
        """
        print("\n" + "=" * 60)
        print("检查数据文件")
        print("=" * 60)
        print()
        
        # 检查NPZ文件
        npz_file = self.output_dir / 'pems04.npz'
        if npz_file.exists():
            print(f"✅ 找到: pems04.npz ({npz_file.stat().st_size / (1024*1024):.2f} MB)")
            return True
        
        # 检查NPY文件
        flow_file = self.output_dir / 'pems04_flow_sample.npy'
        speed_file = self.output_dir / 'pems04_speed_sample.npy'
        occupancy_file = self.output_dir / 'pems04_occupancy_sample.npy'
        
        if all(f.exists() for f in [flow_file, speed_file, occupancy_file]):
            print(f"✅ 找到示例数据文件")
            print(f"   - {flow_file.name}")
            print(f"   - {speed_file.name}")
            print(f"   - {occupancy_file.name}")
            return True
        
        print("❌ 未找到数据文件")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("PeMS04 交通数据集下载工具")
    print("=" * 60)
    print()
    
    # 创建下载器
    downloader = DataDownloader()
    
    # 检查是否已有数据
    if downloader.check_data_files():
        print("\n✅ 数据已就绪，无需重新下载")
        response = input("\n是否重新下载？(y/N): ").strip().lower()
        if response != 'y':
            print("跳过下载")
            return
    
    print("\n请选择下载选项:")
    print("  1. 下载真实数据集 (PeMS04 NPZ, ~40MB)")
    print("  2. 生成示例数据 (用于快速测试)")
    print("  3. 跳过")
    
    choice = input("\n请输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        print("\n开始下载真实数据集...")
        downloader.download_pems04_npz()
    elif choice == '2':
        print("\n生成示例数据...")
        downloader.download_sample_data()
    else:
        print("\n跳过下载")
    
    # 最终检查
    print()
    downloader.check_data_files()
    
    print("\n" + "=" * 60)
    print("💡 提示:")
    print("  - 数据保存在: data/raw/")
    print("  - 如果下载失败，可以手动下载并放置到上述目录")
    print("  - GitHub: https://github.com/Davidham3/ASTGCN/tree/master/data/PEMS04")
    print("=" * 60)


if __name__ == "__main__":
    main()

