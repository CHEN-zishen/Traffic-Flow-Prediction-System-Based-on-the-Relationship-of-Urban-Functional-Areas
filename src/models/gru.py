"""
GRU预测模型
基于GRU的交通流预测神经网络（对比模型）
"""

import torch
import torch.nn as nn
from typing import Dict, Any
from .base import BasePredictor


class GRUPredictor(BasePredictor):
    """
    GRU交通流预测模型
    
    架构与LSTM类似，使用GRU替代LSTM
    用于性能对比实验
    """
    
    def __init__(
        self,
        input_size: int = 3,
        hidden_size: int = 128,
        num_layers: int = 2,
        output_size: int = 3,
        dropout: float = 0.2,
        bidirectional: bool = False
    ):
        """
        初始化GRU模型
        
        Args:
            input_size: 输入特征维度
            hidden_size: 隐藏层大小
            num_layers: GRU层数
            output_size: 输出维度
            dropout: Dropout比率
            bidirectional: 是否使用双向GRU
        """
        super().__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size
        self.dropout_rate = dropout
        self.bidirectional = bidirectional
        
        # 计算方向系数
        self.num_directions = 2 if bidirectional else 1
        
        # GRU层1
        self.gru1 = nn.GRU(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )
        
        # GRU层2
        self.gru2 = nn.GRU(
            input_size=hidden_size * self.num_directions,
            hidden_size=hidden_size // 2,
            num_layers=1,
            batch_first=True,
            dropout=0,
            bidirectional=False
        )
        
        # Dropout层
        self.dropout = nn.Dropout(dropout)
        
        # 全连接层
        self.fc1 = nn.Linear(hidden_size // 2, 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, output_size)
        
        # 初始化权重
        self._init_weights()
    
    def _init_weights(self):
        """初始化模型权重"""
        for name, param in self.named_parameters():
            if 'weight' in name:
                if 'gru' in name:
                    nn.init.orthogonal_(param)
                else:
                    nn.init.xavier_uniform_(param)
            elif 'bias' in name:
                nn.init.constant_(param, 0)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        前向传播
        
        Args:
            x: 输入张量 (batch, seq_len, input_size)
        
        Returns:
            output: 输出张量 (batch, output_size)
        """
        # GRU层1
        out, h_n = self.gru1(x)
        
        # Dropout
        out = self.dropout(out)
        
        # GRU层2
        out, h_n2 = self.gru2(out)
        
        # 取最后一个时间步的输出
        out = out[:, -1, :]
        
        # Dropout
        out = self.dropout(out)
        
        # 全连接层
        out = self.fc1(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取模型配置
        
        Returns:
            配置字典
        """
        return {
            'model_type': 'GRU',
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
            'num_layers': self.num_layers,
            'output_size': self.output_size,
            'dropout': self.dropout_rate,
            'bidirectional': self.bidirectional
        }


def create_gru_model(config: Dict[str, Any] = None) -> GRUPredictor:
    """
    创建GRU模型的工厂函数
    
    Args:
        config: 配置字典
    
    Returns:
        GRU模型实例
    """
    if config is None:
        from src.utils.config import get_config
        config = get_config('gru.model', config_type='model')
    
    model = GRUPredictor(
        input_size=config.get('input_size', 3),
        hidden_size=config.get('hidden_size', 128),
        num_layers=config.get('num_layers', 2),
        output_size=config.get('output_size', 3),
        dropout=config.get('dropout', 0.2),
        bidirectional=config.get('bidirectional', False)
    )
    
    return model


if __name__ == "__main__":
    # 测试模型
    print("测试GRU模型...")
    
    # 创建模型
    model = GRUPredictor(
        input_size=3,
        hidden_size=128,
        num_layers=2,
        output_size=3,
        dropout=0.2
    )
    
    # 打印模型信息
    model.print_model_info()
    
    # 测试前向传播
    batch_size = 32
    seq_len = 12
    input_size = 3
    
    x = torch.randn(batch_size, seq_len, input_size)
    output = model(x)
    
    print(f"输入形状: {x.shape}")
    print(f"输出形状: {output.shape}")
    print(f"✅ 模型测试通过!")

