-- 修复用户数据，确保所有字段都有默认值
USE traffic_prediction;

-- 更新所有用户的NULL字段为默认值
UPDATE users 
SET 
    prediction_count = COALESCE(prediction_count, 0),
    model_type = COALESCE(model_type, 'lstm'),
    weather_weight = COALESCE(weather_weight, 0.25),
    time_weight = COALESCE(time_weight, 0.25),
    district_weight = COALESCE(district_weight, 0.25),
    other_weight = COALESCE(other_weight, 0.25),
    use_gpu = COALESCE(use_gpu, 0),
    multi_predict = COALESCE(multi_predict, 0),
    receive_email = COALESCE(receive_email, 1),
    nickname = COALESCE(nickname, username),
    avatar = COALESCE(avatar, NULL),
    login_count = COALESCE(login_count, 0);

-- 查看更新后的数据
SELECT 
    id,
    username,
    email,
    nickname,
    prediction_count,
    model_type,
    weather_weight,
    use_gpu,
    receive_email
FROM users;

SELECT '✅ 用户数据修复完成！' AS Result;

