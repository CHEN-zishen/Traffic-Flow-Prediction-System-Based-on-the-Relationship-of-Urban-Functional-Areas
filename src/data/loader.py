"""
交通数据加载器
负责加载和解析PeMS04数据集
"""

import numpy as np
from pathlib import Path
from typing import Dict, Tuple, Optional
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import config


class TrafficDataLoader:
    """交通数据加载器"""
    
    def __init__(self, data_path: str = None):
        """
        初始化数据加载器
        
        Args:
            data_path: 数据目录路径
        """
        if data_path is None:
            data_path = config.get('paths.data_raw')
        
        self.data_path = Path(data_path)
        
        if not self.data_path.exists():
            raise FileNotFoundError(f"数据目录不存在: {self.data_path}")
    
    def load_pems04_npz(self) -> Dict[str, np.ndarray]:
        """
        加载PeMS04数据集（NPZ格式）
        
        Returns:
            包含flow, speed, occupancy的字典
        """
        npz_file = self.data_path / 'pems04.npz'
        
        if not npz_file.exists():
            raise FileNotFoundError(
                f"数据文件不存在: {npz_file}\n"
                f"请先运行: python src/scripts/download_data.py"
            )
        
        print(f"[加载] 加载数据: {npz_file}")
        
        # 加载NPZ文件
        data = np.load(npz_file)
        
        # 提取数据
        # PeMS04数据格式: (num_timesteps, num_sensors, num_features)
        raw_data = data['data']  # (16992, 307, 3)
        
        print(f"[OK] 数据加载成功")
        print(f"   形状: {raw_data.shape}")
        print(f"   时间步: {raw_data.shape[0]}")
        print(f"   传感器: {raw_data.shape[1]}")
        print(f"   特征数: {raw_data.shape[2]}")
        
        # 分离特征
        # 注意：PeMS04 NPZ格式通常是 [flow, occupancy, speed]
        result = {
            'flow': raw_data[:, :, 0],        # (16992, 307)
            'occupancy': raw_data[:, :, 1],   # (16992, 307)
            'speed': raw_data[:, :, 2],       # (16992, 307)
        }
        
        # 打印统计信息
        print(f"\n[统计] 数据统计:")
        for key, value in result.items():
            print(f"   {key:12s}: shape={value.shape}, "
                  f"mean={value.mean():.2f}, "
                  f"std={value.std():.2f}, "
                  f"min={value.min():.2f}, "
                  f"max={value.max():.2f}")
        
        return result
    
    def load_pems04_npy(self) -> Dict[str, np.ndarray]:
        """
        加载PeMS04数据集（NPY格式）
        
        Returns:
            包含flow, speed, occupancy的字典
        """
        flow_file = self.data_path / 'pems04_flow_sample.npy'
        speed_file = self.data_path / 'pems04_speed_sample.npy'
        occupancy_file = self.data_path / 'pems04_occupancy_sample.npy'
        
        # 检查文件是否存在
        if not all(f.exists() for f in [flow_file, speed_file, occupancy_file]):
            raise FileNotFoundError(
                f"数据文件不完整:\n"
                f"  - {flow_file}\n"
                f"  - {speed_file}\n"
                f"  - {occupancy_file}\n"
                f"请先运行: python src/scripts/download_data.py"
            )
        
        print(f"[加载] 加载数据（NPY格式）")
        
        # 加载数据
        flow = np.load(flow_file)
        speed = np.load(speed_file)
        occupancy = np.load(occupancy_file)
        
        result = {
            'flow': flow,
            'speed': speed,
            'occupancy': occupancy
        }
        
        print(f"[OK] 数据加载成功")
        print(f"   Flow: {flow.shape}")
        print(f"   Speed: {speed.shape}")
        print(f"   Occupancy: {occupancy.shape}")
        
        return result
    
    def load_data(self, format: str = 'auto') -> Dict[str, np.ndarray]:
        """
        自动检测并加载数据
        
        Args:
            format: 数据格式 ('auto', 'npz', 'npy')
        
        Returns:
            数据字典
        """
        if format == 'auto':
            # 优先尝试NPZ格式
            npz_file = self.data_path / 'pems04.npz'
            if npz_file.exists():
                return self.load_pems04_npz()
            else:
                return self.load_pems04_npy()
        elif format == 'npz':
            return self.load_pems04_npz()
        elif format == 'npy':
            return self.load_pems04_npy()
        else:
            raise ValueError(f"不支持的格式: {format}")
    
    def load_subset(
        self,
        sensors: Optional[list] = None,
        time_range: Optional[Tuple[int, int]] = None
    ) -> Dict[str, np.ndarray]:
        """
        加载数据子集
        
        Args:
            sensors: 传感器ID列表（可选）
            time_range: 时间范围 (start, end)（可选）
        
        Returns:
            数据子集
        """
        # 加载完整数据
        data = self.load_data()
        
        # 选择传感器
        if sensors is not None:
            for key in data:
                data[key] = data[key][:, sensors]
        
        # 选择时间范围
        if time_range is not None:
            start, end = time_range
            for key in data:
                data[key] = data[key][start:end, :]
        
        print(f"[OK] 加载数据子集")
        if sensors is not None:
            print(f"   传感器: {len(sensors)}个")
        if time_range is not None:
            print(f"   时间范围: {time_range[0]} - {time_range[1]}")
        
        return data
    
    def get_data_info(self) -> Dict:
        """
        获取数据集信息
        
        Returns:
            数据集信息字典
        """
        data = self.load_data()
        
        info = {
            'num_timesteps': data['flow'].shape[0],
            'num_sensors': data['flow'].shape[1],
            'features': list(data.keys()),
            'time_interval': '5 minutes',
            'dataset': 'PeMS04'
        }
        
        return info


def load_pems04_data(data_path: str = None) -> Dict[str, np.ndarray]:
    """
    便捷函数：加载PeMS04数据
    
    Args:
        data_path: 数据路径
    
    Returns:
        数据字典
    """
    loader = TrafficDataLoader(data_path)
    return loader.load_data()


if __name__ == "__main__":
    # 测试数据加载
    print("=" * 60)
    print("测试交通数据加载器")
    print("=" * 60)
    print()
    
    try:
        # 创建加载器
        loader = TrafficDataLoader()
        
        # 加载数据
        data = loader.load_data()
        
        print(f"\n✅ 数据加载测试通过!")
        print(f"\n数据键: {list(data.keys())}")
        
        # 获取数据集信息
        info = loader.get_data_info()
        print(f"\n📋 数据集信息:")
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # 测试子集加载
        print(f"\n测试子集加载...")
        subset = loader.load_subset(
            sensors=list(range(10)),
            time_range=(0, 100)
        )
        print(f"子集shape: {subset['flow'].shape}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

