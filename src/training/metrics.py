"""评估指标计算"""
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score

def calculate_mae(y_true, y_pred):
    """计算MAE"""
    return mean_absolute_error(y_true, y_pred)

def calculate_rmse(y_true, y_pred):
    """计算RMSE"""
    return np.sqrt(mean_squared_error(y_true, y_pred))

def calculate_mape(y_true, y_pred):
    """计算MAPE"""
    return np.mean(np.abs((y_true - y_pred) / (y_true + 1e-8))) * 100

def calculate_accuracy(y_true, y_pred):
    """计算分类准确率"""
    return accuracy_score(y_true, y_pred)

