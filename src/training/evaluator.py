"""模型评估器"""
import torch
import numpy as np
from .metrics import calculate_mae, calculate_rmse, calculate_mape

class ModelEvaluator:
    def __init__(self, model, test_loader, device='cpu'):
        self.model = model
        self.test_loader = test_loader
        self.device = torch.device(device)
    
    def evaluate(self):
        """评估模型"""
        self.model.eval()
        all_preds, all_targets = [], []
        
        with torch.no_grad():
            for batch_x, batch_y in self.test_loader:
                batch_x = batch_x.to(self.device)
                outputs = self.model(batch_x)
                
                all_preds.append(outputs.cpu().numpy())
                if batch_y.dim() == 3:
                    all_targets.append(batch_y[:, 0, :].numpy())
                else:
                    all_targets.append(batch_y.numpy())
        
        preds = np.concatenate(all_preds)
        targets = np.concatenate(all_targets)
        
        return {
            'mae': calculate_mae(targets, preds),
            'rmse': calculate_rmse(targets, preds),
            'mape': calculate_mape(targets, preds)
        }

