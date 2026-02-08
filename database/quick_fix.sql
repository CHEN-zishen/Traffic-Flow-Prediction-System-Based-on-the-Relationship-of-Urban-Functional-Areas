-- 快速修复predictions表
USE traffic_db;

DROP TABLE IF EXISTS predictions;

CREATE TABLE predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    sensor_id VARCHAR(50) NOT NULL COMMENT '传感器ID',
    prediction_time DATETIME NOT NULL COMMENT '预测时间',
    target_time DATETIME NOT NULL COMMENT '目标时间',
    
    flow_prediction FLOAT COMMENT '流量预测值',
    flow_actual FLOAT DEFAULT NULL COMMENT '实际流量值',
    
    density_prediction FLOAT COMMENT '密度预测值',
    density_actual FLOAT DEFAULT NULL COMMENT '实际密度值',
    
    congestion_prediction ENUM('畅通', '正常', '拥堵', '严重拥堵') COMMENT '拥堵状态预测',
    congestion_actual ENUM('畅通', '正常', '拥堵', '严重拥堵') DEFAULT NULL COMMENT '实际拥堵状态',
    
    confidence FLOAT COMMENT '预测置信度',
    model_version VARCHAR(50) COMMENT '使用的模型版本',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    INDEX idx_sensor_id (sensor_id),
    INDEX idx_prediction_time (prediction_time),
    INDEX idx_target_time (target_time),
    INDEX idx_created_at (created_at),
    INDEX idx_model_version (model_version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='预测结果表';

SELECT '表已修复！congestion_prediction枚举值: 畅通, 正常, 拥堵, 严重拥堵' AS message;
SELECT 'sensor_id类型已更改为VARCHAR(50)' AS message;

