"""GRU模型训练脚本"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.data.loader import TrafficDataLoader
from src.data.preprocessor import TrafficDataPreprocessor
from src.data.dataset import prepare_traffic_data, create_dataloaders
from src.models.gru import GRUPredictor
from src.training.trainer import ModelTrainer

def main():
    print("=== 智能交通流预测系统 - GRU模型训练 ===\n")
    
    # 1. 加载数据
    print("1. 加载数据...")
    loader = TrafficDataLoader()
    data = loader.load_data()
    
    # 2. 预处理
    print("\n2. 数据预处理...")
    preprocessor = TrafficDataPreprocessor()
    processed = preprocessor.process_data(data)
    
    # 3. 准备数据集
    print("\n3. 准备数据集...")
    train_data, val_data, test_data = prepare_traffic_data(processed, simplified=True)
    train_loader, val_loader, test_loader = create_dataloaders(
        train_data, val_data, test_data, batch_size=64, simplified=True
    )
    
    # 4. 创建GRU模型
    print("\n4. 创建GRU模型...")
    model = GRUPredictor(
        input_size=3,
        hidden_size=128,
        num_layers=2,
        output_size=3,
        dropout=0.2
    )
    
    print(f"   模型参数量: {sum(p.numel() for p in model.parameters()):,}")
    
    # 5. 训练配置
    config_dict = {
        'learning_rate': 0.001,
        'optimizer': 'Adam',
        'weight_decay': 0.00001,
        'batch_size': 64,
        'early_stopping': {'patience': 10},
        'scheduler': {'type': 'ReduceLROnPlateau', 'patience': 5}
    }
    
    # 6. 开始训练
    print("\n5. 开始训练GRU模型...")
    trainer = ModelTrainer(model, train_loader, val_loader, config_dict, 'gru')
    results = trainer.train(epochs=50)
    
    print("\n" + "="*60)
    print("✅ GRU模型训练完成！")
    print("="*60)
    print(f"📊 最佳验证损失: {results['best_val_loss']:.4f}")
    print(f"📊 最佳Epoch: {results.get('best_epoch', 'N/A')}")
    print(f"💾 模型保存位置: data/models/best/gru_best.pth")
    print(f"💾 检查点保存位置: data/models/checkpoints/gru_epoch_*.pth")
    print("="*60)

if __name__ == "__main__":
    main()

