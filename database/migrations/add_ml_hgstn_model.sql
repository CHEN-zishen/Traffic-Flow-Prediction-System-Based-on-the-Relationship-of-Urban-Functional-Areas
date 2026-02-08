-- 添加 ML-HGSTN 模型支持
-- 执行日期：2024-11-08
-- 说明：更新 model_type 字段注释，支持新的 ML-HGSTN 模型

USE traffic_prediction;

-- 修改 model_type 字段，更新注释以支持新模型
ALTER TABLE users 
MODIFY COLUMN model_type VARCHAR(20) DEFAULT 'lstm' 
COMMENT '选择的模型类型：lstm/gru/ml-hgstn/transformer/tcn';

-- 验证修改结果
SELECT 
    COLUMN_NAME AS '字段名',
    COLUMN_TYPE AS '类型',
    COLUMN_DEFAULT AS '默认值',
    COLUMN_COMMENT AS '注释'
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'traffic_prediction' 
  AND TABLE_NAME = 'users' 
  AND COLUMN_NAME = 'model_type';

SELECT '✅ ML-HGSTN 模型支持已添加！' AS message;


