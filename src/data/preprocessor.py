"""
交通数据预处理器
数据清洗、归一化、特征工程
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler
from typing import Dict, Tuple, Optional
import pickle
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.utils.config import config


class TrafficDataPreprocessor:
    """交通数据预处理器"""
    
    def __init__(self):
        """初始化预处理器"""
        self.scaler = None
        self.scaler_type = None
    
    def handle_missing_values(
        self,
        data: np.ndarray,
        method: str = 'interpolate'
    ) -> np.ndarray:
        """
        处理缺失值
        
        Args:
            data: 输入数据 (timesteps, sensors)
            method: 处理方法 ('interpolate', 'forward_fill', 'backward_fill', 'mean')
        
        Returns:
            处理后的数据
        """
        print(f"🔧 处理缺失值 (方法: {method})...")
        
        # 统计缺失值
        nan_count = np.isnan(data).sum()
        if nan_count == 0:
            print(f"   ✓ 无缺失值")
            return data
        
        print(f"   发现缺失值: {nan_count} ({nan_count/data.size*100:.2f}%)")
        
        df = pd.DataFrame(data)
        
        if method == 'interpolate':
            # 线性插值
            df = df.interpolate(method='linear', axis=0, limit_direction='both')
        elif method == 'forward_fill':
            # 前向填充
            df = df.fillna(method='ffill')
        elif method == 'backward_fill':
            # 后向填充
            df = df.fillna(method='bfill')
        elif method == 'mean':
            # 均值填充
            df = df.fillna(df.mean())
        else:
            raise ValueError(f"不支持的方法: {method}")
        
        # 如果还有缺失值，使用0填充
        df = df.fillna(0)
        
        result = df.values
        print(f"   ✓ 缺失值处理完成")
        
        return result
    
    def detect_outliers(
        self,
        data: np.ndarray,
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> np.ndarray:
        """
        检测异常值
        
        Args:
            data: 输入数据
            method: 检测方法 ('iqr', 'zscore')
            threshold: 阈值
        
        Returns:
            异常值掩码（True表示异常）
        """
        print(f"🔍 检测异常值 (方法: {method}, 阈值: {threshold})...")
        
        if method == 'iqr':
            # IQR方法
            Q1 = np.percentile(data, 25, axis=0)
            Q3 = np.percentile(data, 75, axis=0)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            outliers = (data < lower_bound) | (data > upper_bound)
        
        elif method == 'zscore':
            # Z-score方法
            mean = np.mean(data, axis=0)
            std = np.std(data, axis=0)
            z_scores = np.abs((data - mean) / (std + 1e-8))
            
            outliers = z_scores > threshold
        
        else:
            raise ValueError(f"不支持的方法: {method}")
        
        outlier_count = outliers.sum()
        print(f"   检测到异常值: {outlier_count} ({outlier_count/data.size*100:.2f}%)")
        
        return outliers
    
    def handle_outliers(
        self,
        data: np.ndarray,
        action: str = 'clip',
        method: str = 'iqr',
        threshold: float = 1.5
    ) -> np.ndarray:
        """
        处理异常值
        
        Args:
            data: 输入数据
            action: 处理动作 ('clip', 'remove', 'interpolate')
            method: 检测方法
            threshold: 阈值
        
        Returns:
            处理后的数据
        """
        outliers = self.detect_outliers(data, method, threshold)
        
        if action == 'clip':
            # 裁剪到合理范围
            Q1 = np.percentile(data, 25, axis=0)
            Q3 = np.percentile(data, 75, axis=0)
            IQR = Q3 - Q1
            lower_bound = Q1 - threshold * IQR
            upper_bound = Q3 + threshold * IQR
            
            data = np.clip(data, lower_bound, upper_bound)
            print(f"   ✓ 异常值已裁剪")
        
        elif action == 'interpolate':
            # 使用插值替换
            data_copy = data.copy()
            data_copy[outliers] = np.nan
            data = self.handle_missing_values(data_copy, method='interpolate')
            print(f"   ✓ 异常值已插值")
        
        elif action == 'remove':
            print(f"   ⚠️ 'remove'动作暂不支持，使用'clip'替代")
            return self.handle_outliers(data, action='clip', method=method, threshold=threshold)
        
        return data
    
    def normalize(
        self,
        data: np.ndarray,
        method: str = 'minmax',
        feature_range: Tuple[float, float] = (0, 1)
    ) -> np.ndarray:
        """
        数据归一化
        
        Args:
            data: 输入数据 (timesteps, sensors)
            method: 归一化方法 ('minmax', 'standard', 'robust')
            feature_range: MinMaxScaler的范围
        
        Returns:
            归一化后的数据
        """
        print(f"📊 数据归一化 (方法: {method})...")
        
        self.scaler_type = method
        
        # 重塑数据以适应scaler
        original_shape = data.shape
        data_reshaped = data.reshape(-1, 1) if data.ndim == 2 else data
        
        if method == 'minmax':
            self.scaler = MinMaxScaler(feature_range=feature_range)
        elif method == 'standard':
            self.scaler = StandardScaler()
        elif method == 'robust':
            self.scaler = RobustScaler()
        else:
            raise ValueError(f"不支持的归一化方法: {method}")
        
        # 对每个传感器独立归一化
        normalized = np.zeros_like(data)
        for i in range(data.shape[1]):
            sensor_data = data[:, i].reshape(-1, 1)
            normalized[:, i] = self.scaler.fit_transform(sensor_data).flatten()
        
        print(f"   ✓ 归一化完成")
        print(f"   原始范围: [{data.min():.2f}, {data.max():.2f}]")
        print(f"   归一化范围: [{normalized.min():.2f}, {normalized.max():.2f}]")
        
        return normalized
    
    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        """
        反归一化
        
        Args:
            data: 归一化后的数据
        
        Returns:
            原始尺度的数据
        """
        if self.scaler is None:
            raise ValueError("尚未训练scaler，请先调用normalize()")
        
        # 对每个传感器独立反归一化
        denormalized = np.zeros_like(data)
        for i in range(data.shape[1] if data.ndim > 1 else 1):
            if data.ndim > 1:
                sensor_data = data[:, i].reshape(-1, 1)
                denormalized[:, i] = self.scaler.inverse_transform(sensor_data).flatten()
            else:
                denormalized = self.scaler.inverse_transform(data.reshape(-1, 1)).flatten()
        
        return denormalized
    
    def create_congestion_labels(
        self,
        speed: np.ndarray,
        thresholds: Dict[str, float] = None
    ) -> np.ndarray:
        """
        创建拥堵状态标签
        
        Args:
            speed: 速度数据 (timesteps, sensors)
            thresholds: 阈值字典 {'clear': 60, 'slow': 30}
        
        Returns:
            拥堵标签 (0: 畅通, 1: 缓行, 2: 拥堵)
        """
        print(f"🚦 生成拥堵状态标签...")
        
        if thresholds is None:
            thresholds = {'clear': 60, 'slow': 30}
        
        labels = np.zeros_like(speed, dtype=int)
        
        # 畅通: 速度 > 60
        labels[speed > thresholds['clear']] = 0
        
        # 缓行: 30 <= 速度 <= 60
        labels[(speed >= thresholds['slow']) & (speed <= thresholds['clear'])] = 1
        
        # 拥堵: 速度 < 30
        labels[speed < thresholds['slow']] = 2
        
        # 统计各类别数量
        unique, counts = np.unique(labels, return_counts=True)
        label_names = ['畅通', '缓行', '拥堵']
        
        print(f"   标签分布:")
        for label, count in zip(unique, counts):
            percentage = count / labels.size * 100
            print(f"     {label_names[label]}: {count} ({percentage:.1f}%)")
        
        return labels
    
    def save_scaler(self, filepath: str):
        """
        保存归一化器
        
        Args:
            filepath: 保存路径
        """
        if self.scaler is None:
            raise ValueError("尚未训练scaler")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'scaler_type': self.scaler_type
            }, f)
        
        print(f"✅ Scaler已保存: {filepath}")
    
    def load_scaler(self, filepath: str):
        """
        加载归一化器
        
        Args:
            filepath: 文件路径
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.scaler = data['scaler']
            self.scaler_type = data['scaler_type']
        
        print(f"✅ Scaler已加载: {filepath}")
    
    def process_data(
        self,
        data: Dict[str, np.ndarray],
        save_scaler: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        完整的数据预处理流程
        
        Args:
            data: 包含flow, speed, occupancy的字典
            save_scaler: 是否保存scaler
        
        Returns:
            处理后的数据
        """
        print("\n" + "=" * 60)
        print("开始数据预处理")
        print("=" * 60)
        
        processed = {}
        
        # 处理每个特征
        for key in ['flow', 'speed', 'occupancy']:
            if key not in data:
                continue
            
            print(f"\n处理特征: {key}")
            print("-" * 60)
            
            # 1. 处理缺失值
            clean_data = self.handle_missing_values(data[key])
            
            # 2. 处理异常值
            clean_data = self.handle_outliers(clean_data)
            
            # 3. 归一化
            normalized = self.normalize(clean_data)
            
            processed[key] = normalized
        
        # 4. 创建拥堵标签
        if 'speed' in data:
            processed['congestion'] = self.create_congestion_labels(data['speed'])
        
        # 5. 保存scaler
        if save_scaler:
            scaler_path = config.get('paths.data_processed') + 'scaler.pkl'
            self.save_scaler(scaler_path)
        
        print("\n" + "=" * 60)
        print("✅ 数据预处理完成!")
        print("=" * 60)
        
        return processed


if __name__ == "__main__":
    # 测试预处理器
    print("测试数据预处理器...")
    
    from src.data.loader import TrafficDataLoader
    
    # 加载数据
    loader = TrafficDataLoader()
    data = loader.load_data()
    
    # 创建预处理器
    preprocessor = TrafficDataPreprocessor()
    
    # 处理数据
    processed = preprocessor.process_data(data)
    
    print(f"\n处理后的数据:")
    for key, value in processed.items():
        print(f"  {key}: {value.shape}")

