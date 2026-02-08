-- 添加用户个人资料和模型配置字段（兼容版本）
-- 执行日期：2024-11-06
-- 适用于 MySQL 5.7+ 所有版本

USE traffic_prediction;

-- 使用存储过程来安全地添加字段
DELIMITER $$

DROP PROCEDURE IF EXISTS add_column_if_not_exists$$

CREATE PROCEDURE add_column_if_not_exists()
BEGIN
    -- 检查并添加 prediction_count 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'prediction_count'
    ) THEN
        ALTER TABLE users ADD COLUMN prediction_count INT DEFAULT 0 COMMENT '预测次数';
    END IF;

    -- 检查并添加 model_type 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'model_type'
    ) THEN
        ALTER TABLE users ADD COLUMN model_type VARCHAR(20) DEFAULT 'lstm' COMMENT '选择的模型类型：lstm/gru';
    END IF;

    -- 检查并添加 weather_weight 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'weather_weight'
    ) THEN
        ALTER TABLE users ADD COLUMN weather_weight FLOAT DEFAULT 0.25 COMMENT '天气因素权重';
    END IF;

    -- 检查并添加 time_weight 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'time_weight'
    ) THEN
        ALTER TABLE users ADD COLUMN time_weight FLOAT DEFAULT 0.25 COMMENT '时间段因素权重';
    END IF;

    -- 检查并添加 district_weight 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'district_weight'
    ) THEN
        ALTER TABLE users ADD COLUMN district_weight FLOAT DEFAULT 0.25 COMMENT '城市功能区因素权重';
    END IF;

    -- 检查并添加 other_weight 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'other_weight'
    ) THEN
        ALTER TABLE users ADD COLUMN other_weight FLOAT DEFAULT 0.25 COMMENT '其他因素权重';
    END IF;

    -- 检查并添加 use_gpu 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'use_gpu'
    ) THEN
        ALTER TABLE users ADD COLUMN use_gpu BOOLEAN DEFAULT FALSE COMMENT '是否使用GPU加速';
    END IF;

    -- 检查并添加 multi_predict 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'multi_predict'
    ) THEN
        ALTER TABLE users ADD COLUMN multi_predict BOOLEAN DEFAULT FALSE COMMENT '是否多次预测';
    END IF;

    -- 检查并添加 receive_email 字段
    IF NOT EXISTS (
        SELECT * FROM information_schema.COLUMNS 
        WHERE TABLE_SCHEMA = 'traffic_prediction' 
        AND TABLE_NAME = 'users' 
        AND COLUMN_NAME = 'receive_email'
    ) THEN
        ALTER TABLE users ADD COLUMN receive_email BOOLEAN DEFAULT TRUE COMMENT '是否接收邮件通知';
    END IF;

END$$

DELIMITER ;

-- 调用存储过程来添加字段
CALL add_column_if_not_exists();

-- 删除存储过程
DROP PROCEDURE IF EXISTS add_column_if_not_exists;

-- 为现有用户更新默认值（只更新NULL值）
UPDATE users SET prediction_count = 0 WHERE prediction_count IS NULL;
UPDATE users SET model_type = 'lstm' WHERE model_type IS NULL;
UPDATE users SET weather_weight = 0.25 WHERE weather_weight IS NULL;
UPDATE users SET time_weight = 0.25 WHERE time_weight IS NULL;
UPDATE users SET district_weight = 0.25 WHERE district_weight IS NULL;
UPDATE users SET other_weight = 0.25 WHERE other_weight IS NULL;
UPDATE users SET use_gpu = FALSE WHERE use_gpu IS NULL;
UPDATE users SET multi_predict = FALSE WHERE multi_predict IS NULL;
UPDATE users SET receive_email = TRUE WHERE receive_email IS NULL;

SELECT '✅ 用户表字段添加完成！' AS message;

