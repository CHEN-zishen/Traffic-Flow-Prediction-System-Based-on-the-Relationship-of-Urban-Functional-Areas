-- 简化版：直接添加字段（如果已存在会报错，但可以忽略）
USE traffic_prediction;

-- 添加预测次数字段
ALTER TABLE users ADD COLUMN prediction_count INT DEFAULT 0 COMMENT '预测次数';

-- 添加模型配置相关字段
ALTER TABLE users ADD COLUMN model_type VARCHAR(20) DEFAULT 'lstm' COMMENT '选择的模型类型：lstm/gru';
ALTER TABLE users ADD COLUMN weather_weight FLOAT DEFAULT 0.25 COMMENT '天气因素权重';
ALTER TABLE users ADD COLUMN time_weight FLOAT DEFAULT 0.25 COMMENT '时间段因素权重';
ALTER TABLE users ADD COLUMN district_weight FLOAT DEFAULT 0.25 COMMENT '城市功能区因素权重';
ALTER TABLE users ADD COLUMN other_weight FLOAT DEFAULT 0.25 COMMENT '其他因素权重';
ALTER TABLE users ADD COLUMN use_gpu TINYINT(1) DEFAULT 0 COMMENT '是否使用GPU加速';
ALTER TABLE users ADD COLUMN multi_predict TINYINT(1) DEFAULT 0 COMMENT '是否多次预测';

-- 添加账号设置字段
ALTER TABLE users ADD COLUMN receive_email TINYINT(1) DEFAULT 1 COMMENT '是否接收邮件通知';

-- 为现有用户更新默认值
UPDATE users SET 
    prediction_count = 0,
    model_type = 'lstm',
    weather_weight = 0.25,
    time_weight = 0.25,
    district_weight = 0.25,
    other_weight = 0.25,
    use_gpu = 0,
    multi_predict = 0,
    receive_email = 1
WHERE prediction_count IS NULL OR model_type IS NULL;

SELECT '✅ 字段添加完成！' AS message;

