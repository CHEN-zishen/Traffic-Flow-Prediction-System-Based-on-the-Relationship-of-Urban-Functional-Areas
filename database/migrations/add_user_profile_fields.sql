-- 添加用户个人资料和模型配置字段
-- 执行日期：2024-11-06

USE traffic_prediction;

-- 添加预测次数字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS prediction_count INT DEFAULT 0 COMMENT '预测次数';

-- 添加模型配置相关字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS model_type VARCHAR(20) DEFAULT 'lstm' COMMENT '选择的模型类型：lstm/gru';
ALTER TABLE users ADD COLUMN IF NOT EXISTS weather_weight FLOAT DEFAULT 0.25 COMMENT '天气因素权重';
ALTER TABLE users ADD COLUMN IF NOT EXISTS time_weight FLOAT DEFAULT 0.25 COMMENT '时间段因素权重';
ALTER TABLE users ADD COLUMN IF NOT EXISTS district_weight FLOAT DEFAULT 0.25 COMMENT '城市功能区因素权重';
ALTER TABLE users ADD COLUMN IF NOT EXISTS other_weight FLOAT DEFAULT 0.25 COMMENT '其他因素权重';
ALTER TABLE users ADD COLUMN IF NOT EXISTS use_gpu BOOLEAN DEFAULT FALSE COMMENT '是否使用GPU加速';
ALTER TABLE users ADD COLUMN IF NOT EXISTS multi_predict BOOLEAN DEFAULT FALSE COMMENT '是否多次预测';

-- 添加账号设置字段
ALTER TABLE users ADD COLUMN IF NOT EXISTS receive_email BOOLEAN DEFAULT TRUE COMMENT '是否接收邮件通知';

-- 为现有用户设置默认值
UPDATE users SET 
    prediction_count = 0,
    model_type = 'lstm',
    weather_weight = 0.25,
    time_weight = 0.25,
    district_weight = 0.25,
    other_weight = 0.25,
    use_gpu = FALSE,
    multi_predict = FALSE,
    receive_email = TRUE
WHERE prediction_count IS NULL;

SELECT '用户表字段添加完成！' AS message;

