-- 为历史预测数据添加用户关联
USE traffic_prediction;

-- 1. 添加 user_id 字段
ALTER TABLE city_predictions 
ADD COLUMN user_id INT DEFAULT NULL COMMENT '用户ID' AFTER id;

-- 2. 添加索引
ALTER TABLE city_predictions 
ADD INDEX idx_user_id (user_id);

-- 3. 查看当前历史预测数据总数
SELECT 
    '当前历史预测数据总数' AS info,
    COUNT(*) AS total_count
FROM city_predictions;

-- 4. 统计每个用户现有的预测次数（根据users表中的prediction_count）
SELECT 
    id,
    username,
    prediction_count AS current_count
FROM users
ORDER BY prediction_count DESC;

-- 5. 说明
SELECT '
✅ user_id 字段已添加到 city_predictions 表！

📊 关于历史数据：
- 旧的预测记录 user_id 为 NULL（因为当时没记录）
- 新的预测记录会自动关联到用户
- 个人中心只统计有 user_id 的记录

💡 建议：
如果想把现有历史数据都关联到admin用户，运行：
UPDATE city_predictions SET user_id = 1 WHERE user_id IS NULL;
（假设admin用户的ID是1）
' AS message;

