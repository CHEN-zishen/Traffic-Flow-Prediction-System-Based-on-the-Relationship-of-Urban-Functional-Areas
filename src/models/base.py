"""
基础模型类
定义所有预测模型的通用接口
"""

import torch
import torch.nn as nn
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class BasePredictor(nn.Module, ABC):
    """预测模型基类"""
    
    def __init__(self):
        super().__init__()
        self.model_name = self.__class__.__name__
    
    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x: 输入张量 (batch, seq_len, input_size)
        
        Returns:
            输出张量 (batch, output_size)
        """
        pass
    
    def save_model(self, filepath: str):
        """
        保存模型
        
        Args:
            filepath: 保存路径
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        torch.save({
            'model_name': self.model_name,
            'model_state_dict': self.state_dict(),
            'config': self.get_config(),
        }, filepath)
        
        print(f"✅ 模型已保存: {filepath}")
    
    def load_model(self, filepath: str, map_location='cpu'):
        """
        加载模型
        
        Args:
            filepath: 模型文件路径
            map_location: 设备映射
        """
        checkpoint = torch.load(filepath, map_location=map_location)
        self.load_state_dict(checkpoint['model_state_dict'])
        print(f"✅ 模型已加载: {filepath}")
        
        return checkpoint.get('config', {})
    
    @abstractmethod
    def get_config(self) -> Dict[str, Any]:
        """
        获取模型配置
        
        Returns:
            配置字典
        """
        pass
    
    def count_parameters(self) -> int:
        """
        统计模型参数数量
        
        Returns:
            参数总数
        """
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
    
    def print_model_info(self):
        """打印模型信息"""
        print(f"\n{'='*60}")
        print(f"模型: {self.model_name}")
        print(f"{'='*60}")
        print(f"参数量: {self.count_parameters():,}")
        print(f"配置: {self.get_config()}")
        print(f"{'='*60}\n")

