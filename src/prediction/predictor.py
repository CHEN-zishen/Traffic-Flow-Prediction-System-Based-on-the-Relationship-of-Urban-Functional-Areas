"""交通流预测器"""
import torch
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.lstm import LSTMPredictor
from src.models.gru import GRUPredictor


class TrafficPredictor:
    """交通流预测器"""
    
    def __init__(self, model_path: str, model_type: str = 'lstm', device: str = None):
        """
        初始化预测器
        
        Args:
            model_path: 模型文件路径
            model_type: 模型类型（lstm/gru）
            device: 计算设备
        """
        self.model_type = model_type
        self.device = torch.device(device if device else 
                                   ('cuda' if torch.cuda.is_available() else 'cpu'))
        
        # 加载模型
        self.model = self._load_model(model_path)
        self.model.eval()
        
        print(f"✅ 预测器初始化完成")
        print(f"   模型类型: {model_type.upper()}")
        print(f"   设备: {self.device}")
    
    def _load_model(self, model_path: str):
        """加载模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # 从配置创建模型
        config = checkpoint.get('config', {})
        input_size = config.get('input_size', 3)
        hidden_size = config.get('hidden_size', 128)
        num_layers = config.get('num_layers', 2)
        output_size = config.get('output_size', 3)
        
        if self.model_type == 'lstm':
            model = LSTMPredictor(input_size, hidden_size, num_layers, output_size)
        else:
            model = GRUPredictor(input_size, hidden_size, num_layers, output_size)
        
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(self.device)
        
        return model
    
    def predict(
        self, 
        input_data: np.ndarray, 
        sensor_id: str = None,
        save_to_db: bool = False,
        target_time: datetime = None
    ) -> dict:
        """
        预测交通流
        
        Args:
            input_data: 输入数据 shape=(seq_len, features) 或 (batch, seq_len, features)
            sensor_id: 传感器ID（用于数据库保存）
            save_to_db: 是否保存到数据库
            target_time: 目标预测时间
        
        Returns:
            预测结果字典
        """
        # 转换为tensor
        if input_data.ndim == 2:
            input_data = input_data[np.newaxis, :]  # 添加batch维度
        
        input_tensor = torch.FloatTensor(input_data).to(self.device)
        
        # 预测
        prediction_start_time = datetime.now()
        with torch.no_grad():
            output = self.model(input_tensor)
        
        # 转换为numpy
        prediction = output.cpu().numpy()[0]  # 移除batch维度
        
        # 解析预测结果
        flow_pred = float(prediction[0])
        density_pred = float(prediction[1]) if len(prediction) > 1 else 0.0
        speed_pred = float(prediction[2]) if len(prediction) > 2 else 0.0
        
        # 计算拥堵状态
        congestion_status = self._calculate_congestion(flow_pred, density_pred)
        
        result = {
            'flow': flow_pred,
            'density': density_pred,
            'speed': speed_pred,
            'congestion_status': congestion_status,
            'congestion_level': self._get_congestion_level(congestion_status),
            'confidence': 0.85,  # 简化版本，实际应该基于模型不确定性
            'prediction_time': prediction_start_time.isoformat(),
            'model_type': self.model_type.upper(),
            'sensor_id': sensor_id
        }
        
        # 保存到数据库
        if save_to_db and sensor_id:
            self._save_to_database(result, target_time or prediction_start_time)
        
        return result
    
    def _save_to_database(self, result: dict, target_time: datetime):
        """保存预测结果到数据库"""
        try:
            from src.utils.db_utils import get_db_manager
            db = get_db_manager()
            
            db.create_prediction({
                'sensor_id': result['sensor_id'],
                'prediction_time': datetime.fromisoformat(result['prediction_time']),
                'target_time': target_time,
                'flow_prediction': result['flow'],
                'density_prediction': result['density'],
                'congestion_prediction': result['congestion_level'],  # 使用字符串而不是状态码
                'confidence': result['confidence'],
                'model_version': result['model_type']
            })
            print(f"[DB] 预测结果已保存到数据库: sensor_id={result['sensor_id']}")
        except Exception as e:
            # 数据库保存失败不应影响预测
            print(f"[ERROR] 保存预测结果到数据库失败: {e}")
            import traceback
            traceback.print_exc()
    
    def predict_batch(self, input_data: np.ndarray) -> list:
        """批量预测"""
        if input_data.ndim == 2:
            input_data = input_data[np.newaxis, :]
        
        input_tensor = torch.FloatTensor(input_data).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
        
        predictions = outputs.cpu().numpy()
        
        results = []
        for pred in predictions:
            flow_pred = float(pred[0])
            density_pred = float(pred[1]) if len(pred) > 1 else 0.0
            congestion = self._calculate_congestion(flow_pred, density_pred)
            
            results.append({
                'flow': flow_pred,
                'density': density_pred,
                'congestion_status': congestion,
                'congestion_level': self._get_congestion_level(congestion)
            })
        
        return results
    
    def _calculate_congestion(self, flow: float, density: float) -> int:
        """
        计算拥堵状态
        0: 畅通, 1: 正常, 2: 拥堵, 3: 严重拥堵
        
        根据实际模型输出调整阈值：
        - 模型输出的density范围约为 0.2 - 2.7
        - 不是传统的0-1占有率，而是归一化后的密度值
        """
        # 基于实际模型输出范围调整的阈值
        if density < 0.8:
            return 0  # 畅通: density < 0.8
        elif density < 1.5:
            return 1  # 正常: 0.8 <= density < 1.5
        elif density < 2.2:
            return 2  # 拥堵: 1.5 <= density < 2.2
        else:
            return 3  # 严重拥堵: density >= 2.2
    
    def _get_congestion_level(self, status: int) -> str:
        """获取拥堵等级描述"""
        levels = {0: '畅通', 1: '正常', 2: '拥堵', 3: '严重拥堵'}
        return levels.get(status, '未知')


def create_predictor(model_name: str = 'lstm') -> TrafficPredictor:
    """
    创建预测器的工厂函数
    
    Args:
        model_name: 模型名称
    
    Returns:
        预测器实例
    """
    from src.utils.config import config
    
    # 获取最佳模型路径
    best_model_path = Path(config.get('paths.models_best')) / f'{model_name}_best.pth'
    
    if not best_model_path.exists():
        raise FileNotFoundError(f"模型文件不存在: {best_model_path}")
    
    return TrafficPredictor(str(best_model_path), model_name)


if __name__ == "__main__":
    print("测试预测器...")
    
    # 生成测试数据
    test_data = np.random.randn(12, 3)  # 12个时间步，3个特征
    
    print(f"\n输入形状: {test_data.shape}")
    print(f"输入数据:\n{test_data}")
    
    # 注意：需要先训练模型才能测试预测器
    # predictor = create_predictor('lstm')
    # result = predictor.predict(test_data)
    # print(f"\n预测结果: {result}")
    
    print("\n⚠️  注意：需要先训练模型（python src/scripts/train_model.py）")
    print("   才能使用预测功能")

