-- ============================================
-- 智能交通流预测系统 - 数据库初始化脚本
-- ============================================

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS traffic_db
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE traffic_db;

-- ============================================
-- 表1: predictions（预测结果表）
-- ============================================
CREATE TABLE IF NOT EXISTS predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    sensor_id INT NOT NULL COMMENT '传感器ID',
    prediction_time DATETIME NOT NULL COMMENT '预测时间',
    target_time DATETIME NOT NULL COMMENT '目标时间（预测的未来时间点）',
    
    -- 流量预测
    flow_prediction FLOAT COMMENT '流量预测值',
    flow_actual FLOAT DEFAULT NULL COMMENT '实际流量值（用于后续验证）',
    
    -- 密度预测
    density_prediction FLOAT COMMENT '密度预测值',
    density_actual FLOAT DEFAULT NULL COMMENT '实际密度值',
    
    -- 拥堵状态预测
    congestion_prediction ENUM('畅通', '缓行', '拥堵') COMMENT '拥堵状态预测',
    congestion_actual ENUM('畅通', '缓行', '拥堵') DEFAULT NULL COMMENT '实际拥堵状态',
    
    confidence FLOAT COMMENT '预测置信度',
    model_version VARCHAR(50) COMMENT '使用的模型版本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 索引
    INDEX idx_sensor_time (sensor_id, target_time),
    INDEX idx_prediction_time (prediction_time),
    INDEX idx_created_at (created_at),
    INDEX idx_model_version (model_version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预测结果表';

-- ============================================
-- 表2: training_records（训练记录表）
-- ============================================
CREATE TABLE IF NOT EXISTS training_records (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    model_name VARCHAR(100) NOT NULL COMMENT '模型名称（LSTM/GRU）',
    model_version VARCHAR(50) NOT NULL COMMENT '模型版本号',
    
    -- 训练时间
    start_time DATETIME NOT NULL COMMENT '训练开始时间',
    end_time DATETIME COMMENT '训练结束时间',
    duration_seconds INT COMMENT '训练时长（秒）',
    
    -- 训练参数
    epochs INT COMMENT '训练轮数',
    batch_size INT COMMENT '批大小',
    learning_rate FLOAT COMMENT '学习率',
    optimizer VARCHAR(50) COMMENT '优化器',
    
    -- 训练结果
    train_loss FLOAT COMMENT '最终训练损失',
    val_loss FLOAT COMMENT '最终验证损失',
    best_epoch INT COMMENT '最佳模型对应的epoch',
    
    -- 评估指标
    mae FLOAT COMMENT 'Mean Absolute Error',
    rmse FLOAT COMMENT 'Root Mean Square Error',
    mape FLOAT COMMENT 'Mean Absolute Percentage Error',
    accuracy FLOAT COMMENT '分类准确率',
    
    -- 模型文件
    model_path VARCHAR(255) COMMENT '模型文件路径',
    config_json TEXT COMMENT '完整配置（JSON格式）',
    
    -- 状态
    status ENUM('running', 'completed', 'failed', 'stopped') DEFAULT 'running' COMMENT '训练状态',
    notes TEXT COMMENT '备注',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_model_version (model_version),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型训练记录表';

-- ============================================
-- 表3: api_logs（API调用日志表）
-- ============================================
CREATE TABLE IF NOT EXISTS api_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    endpoint VARCHAR(255) NOT NULL COMMENT 'API端点',
    method VARCHAR(10) NOT NULL COMMENT 'HTTP方法',
    request_ip VARCHAR(50) COMMENT '请求IP',
    request_params TEXT COMMENT '请求参数（JSON）',
    response_status INT COMMENT '响应状态码',
    response_time_ms INT COMMENT '响应时间（毫秒）',
    error_message TEXT COMMENT '错误信息（如有）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 索引
    INDEX idx_endpoint (endpoint),
    INDEX idx_status (response_status),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='API调用日志表';

-- ============================================
-- 表4: model_performance（模型性能对比表）
-- ============================================
CREATE TABLE IF NOT EXISTS model_performance (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    model_name VARCHAR(100) NOT NULL COMMENT '模型名称',
    model_version VARCHAR(50) NOT NULL COMMENT '模型版本',
    test_dataset VARCHAR(100) COMMENT '测试数据集',
    metric_name VARCHAR(50) NOT NULL COMMENT '指标名称（MAE/RMSE等）',
    metric_value FLOAT NOT NULL COMMENT '指标值',
    evaluation_time DATETIME NOT NULL COMMENT '评估时间',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 索引
    INDEX idx_model_metric (model_name, metric_name),
    INDEX idx_evaluation_time (evaluation_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='模型性能对比表';

-- ============================================
-- 表5: system_config（系统配置表）
-- ============================================
CREATE TABLE IF NOT EXISTS system_config (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    config_value TEXT COMMENT '配置值',
    config_type VARCHAR(50) COMMENT '配置类型（string/int/float/json）',
    description VARCHAR(255) COMMENT '配置说明',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 索引
    INDEX idx_key (config_key),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置表';

-- ============================================
-- 初始化系统配置
-- ============================================
INSERT INTO system_config (config_key, config_value, config_type, description) VALUES
('system.version', '1.0.0', 'string', '系统版本'),
('model.default_version', 'lstm_v1.0', 'string', '默认模型版本'),
('prediction.batch_limit', '1000', 'int', '预测批量限制'),
('api.rate_limit', '100', 'int', 'API速率限制（请求/分钟）')
ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP;

-- ============================================
-- 显示表信息
-- ============================================
SHOW TABLES;

SELECT 
    TABLE_NAME as '表名',
    TABLE_ROWS as '行数',
    AVG_ROW_LENGTH as '平均行长度',
    DATA_LENGTH as '数据大小',
    TABLE_COMMENT as '备注'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'traffic_db'
ORDER BY TABLE_NAME;

