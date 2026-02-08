"""
交通流时序数据集
PyTorch Dataset实现
"""

import torch
from torch.utils.data import Dataset, DataLoader
import numpy as np
from typing import Tuple, Dict, Optional
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import config


class TrafficDataset(Dataset):
    """
    交通流时序数据集
    
    支持滑动窗口切割时序数据
    """
    
    def __init__(
        self,
        data: np.ndarray,
        lookback: int = 12,
        horizon: int = 12,
        stride: int = 1
    ):
        """
        初始化数据集
        
        Args:
            data: 输入数据 (timesteps, num_sensors, num_features)
            lookback: 历史窗口大小（输入序列长度）
            horizon: 预测窗口大小（输出序列长度）
            stride: 滑动窗口步长
        """
        self.data = data
        self.lookback = lookback
        self.horizon = horizon
        self.stride = stride
        
        # 计算样本数量
        self.num_samples = (len(data) - lookback - horizon + 1 + stride - 1) // stride
        
        if self.num_samples <= 0:
            raise ValueError(
                f"数据长度不足！需要至少 {lookback + horizon} 个时间步，"
                f"当前只有 {len(data)} 个"
            )
    
    def __len__(self) -> int:
        """返回数据集大小"""
        return self.num_samples
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        获取单个样本
        
        Args:
            idx: 样本索引
        
        Returns:
            (x, y): 输入和目标张量
                x: (lookback, num_sensors, num_features)
                y: (horizon, num_sensors, num_features)
        """
        # 计算实际的起始位置
        start_idx = idx * self.stride
        
        # 输入序列: [start_idx : start_idx + lookback]
        x = self.data[start_idx : start_idx + self.lookback]
        
        # 输出序列: [start_idx + lookback : start_idx + lookback + horizon]
        y = self.data[start_idx + self.lookback : start_idx + self.lookback + self.horizon]
        
        # 转换为Tensor
        x_tensor = torch.FloatTensor(x)
        y_tensor = torch.FloatTensor(y)
        
        return x_tensor, y_tensor


class SimplifiedTrafficDataset(Dataset):
    """
    简化版交通数据集
    
    只预测下一个时间步（而不是整个horizon）
    适合快速训练和测试
    """
    
    def __init__(
        self,
        data: np.ndarray,
        lookback: int = 12
    ):
        """
        初始化数据集
        
        Args:
            data: 输入数据 (timesteps, num_features) 或 (timesteps,)
            lookback: 历史窗口大小
        """
        self.data = data
        self.lookback = lookback
        
        # 确保数据是2D
        if self.data.ndim == 1:
            self.data = self.data.reshape(-1, 1)
        
        self.num_samples = len(data) - lookback
        
        if self.num_samples <= 0:
            raise ValueError(f"数据长度不足！需要至少 {lookback + 1} 个时间步")
    
    def __len__(self) -> int:
        return self.num_samples
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        获取单个样本
        
        Returns:
            (x, y): 输入和目标
                x: (lookback, num_features)
                y: (num_features,) - 下一个时间步
        """
        x = self.data[idx : idx + self.lookback]
        y = self.data[idx + self.lookback]
        
        return torch.FloatTensor(x), torch.FloatTensor(y)


def split_dataset(
    data: np.ndarray,
    train_ratio: float = 0.7,
    val_ratio: float = 0.1,
    test_ratio: float = 0.2
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    划分数据集
    
    Args:
        data: 完整数据
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
    
    Returns:
        (train_data, val_data, test_data)
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
        "比例之和必须等于1"
    
    n = len(data)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_data = data[:train_end]
    val_data = data[train_end:val_end]
    test_data = data[val_end:]
    
    print(f"数据集划分:")
    print(f"   训练集: {len(train_data)} ({len(train_data)/n*100:.1f}%)")
    print(f"   验证集: {len(val_data)} ({len(val_data)/n*100:.1f}%)")
    print(f"   测试集: {len(test_data)} ({len(test_data)/n*100:.1f}%)")
    
    return train_data, val_data, test_data


def create_dataloaders(
    train_data: np.ndarray,
    val_data: np.ndarray,
    test_data: np.ndarray,
    batch_size: int = 64,
    lookback: int = 12,
    horizon: int = 12,
    num_workers: int = 0,
    simplified: bool = False
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    创建数据加载器
    
    Args:
        train_data: 训练数据
        val_data: 验证数据
        test_data: 测试数据
        batch_size: 批大小
        lookback: 历史窗口
        horizon: 预测窗口
        num_workers: 工作进程数
        simplified: 是否使用简化版数据集
    
    Returns:
        (train_loader, val_loader, test_loader)
    """
    # 选择数据集类
    DatasetClass = SimplifiedTrafficDataset if simplified else TrafficDataset
    
    # 创建数据集
    if simplified:
        train_dataset = DatasetClass(train_data, lookback=lookback)
        val_dataset = DatasetClass(val_data, lookback=lookback)
        test_dataset = DatasetClass(test_data, lookback=lookback)
    else:
        train_dataset = DatasetClass(train_data, lookback=lookback, horizon=horizon)
        val_dataset = DatasetClass(val_data, lookback=lookback, horizon=horizon)
        test_dataset = DatasetClass(test_data, lookback=lookback, horizon=horizon)
    
    # 创建数据加载器
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True if torch.cuda.is_available() else False
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers
    )
    
    print(f"\n数据加载器创建完成:")
    print(f"   训练批次: {len(train_loader)}")
    print(f"   验证批次: {len(val_loader)}")
    print(f"   测试批次: {len(test_loader)}")
    print(f"   批大小: {batch_size}")
    
    return train_loader, val_loader, test_loader


def prepare_traffic_data(
    data_dict: Dict[str, np.ndarray],
    features: list = ['flow', 'speed', 'occupancy'],
    train_ratio: float = 0.7,
    val_ratio: float = 0.1,
    simplified: bool = False
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    准备交通数据（特征堆叠 + 划分）
    
    Args:
        data_dict: 数据字典
        features: 要使用的特征列表
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        simplified: 是否简化数据（合并传感器维度）
    
    Returns:
        (train_data, val_data, test_data)
        如果simplified=True: 每个数据形状 (timesteps, num_features)
        如果simplified=False: 每个数据形状 (timesteps, num_sensors, num_features)
    """
    print(f"\n准备交通数据...")
    print(f"使用特征: {features}")
    print(f"简化模式: {simplified}")
    
    # 堆叠特征
    feature_arrays = []
    for feat in features:
        if feat in data_dict:
            # (timesteps, sensors) -> (timesteps, sensors, 1)
            feature_arrays.append(data_dict[feat][..., np.newaxis])
    
    # 堆叠: (timesteps, sensors, num_features)
    combined_data = np.concatenate(feature_arrays, axis=-1)
    
    print(f"合并数据形状: {combined_data.shape}")
    
    # 如果是简化模式，对所有传感器求平均
    if simplified and combined_data.ndim == 3:
        print("简化模式：对所有传感器求平均...")
        combined_data = np.mean(combined_data, axis=1)  # (timesteps, num_features)
        print(f"简化后数据形状: {combined_data.shape}")
    
    # 划分数据集
    test_ratio = 1.0 - train_ratio - val_ratio
    train_data, val_data, test_data = split_dataset(
        combined_data,
        train_ratio,
        val_ratio,
        test_ratio
    )
    
    return train_data, val_data, test_data


if __name__ == "__main__":
    # 测试数据集
    print("=" * 60)
    print("测试交通流数据集")
    print("=" * 60)
    
    # 生成测试数据
    timesteps = 1000
    num_sensors = 10
    num_features = 3
    
    data = np.random.randn(timesteps, num_sensors, num_features)
    
    print(f"\n测试数据形状: {data.shape}")
    
    # 测试TrafficDataset
    print("\n1. 测试 TrafficDataset...")
    dataset = TrafficDataset(data, lookback=12, horizon=12, stride=1)
    print(f"   数据集大小: {len(dataset)}")
    
    x, y = dataset[0]
    print(f"   样本形状: x={x.shape}, y={y.shape}")
    
    # 测试SimplifiedTrafficDataset
    print("\n2. 测试 SimplifiedTrafficDataset...")
    simple_data = data[:, 0, 0]  # 只取一个传感器的一个特征
    simple_dataset = SimplifiedTrafficDataset(simple_data, lookback=12)
    print(f"   数据集大小: {len(simple_dataset)}")
    
    x, y = simple_dataset[0]
    print(f"   样本形状: x={x.shape}, y={y.shape}")
    
    # 测试数据划分和加载器创建
    print("\n3. 测试数据划分和加载器...")
    train_data, val_data, test_data = split_dataset(data)
    
    train_loader, val_loader, test_loader = create_dataloaders(
        train_data, val_data, test_data,
        batch_size=32,
        lookback=12,
        horizon=12
    )
    
    # 测试一个批次
    for batch_x, batch_y in train_loader:
        print(f"\n   批次形状: x={batch_x.shape}, y={batch_y.shape}")
        break
    
    print("\n✅ 数据集测试完成！")

