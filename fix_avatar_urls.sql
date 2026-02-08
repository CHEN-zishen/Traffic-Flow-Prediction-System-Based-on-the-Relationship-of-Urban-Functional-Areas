-- ========================================
-- 头像URL问题排查和修复
-- ========================================

-- 1. 查看所有用户的头像URL
SELECT id, username, avatar, created_at
FROM users
WHERE avatar IS NOT NULL
ORDER BY id;

-- 2. 检查有多少用户的头像URL是测试地址
SELECT COUNT(*) as test_url_count
FROM users
WHERE avatar LIKE '%hrhpdkpuwpxz.sealoshzh.site%';

-- 3. 检查有多少用户的头像URL是相对路径
SELECT COUNT(*) as relative_path_count
FROM users
WHERE avatar LIKE '/static/avatars/%';

-- 4. 【修复】将测试地址的头像URL改为生产地址
UPDATE users 
SET avatar = REPLACE(avatar, 'https://hrhpdkpuwpxz.sealoshzh.site', 'https://yjwkusxabeto.sealoshzh.site'),
    updated_at = NOW()
WHERE avatar LIKE '%hrhpdkpuwpxz.sealoshzh.site%';

-- 5. 【修复】将相对路径改为完整URL
UPDATE users 
SET avatar = CONCAT('https://yjwkusxabeto.sealoshzh.site', avatar),
    updated_at = NOW()
WHERE avatar LIKE '/static/avatars/%';

-- 6. 验证修复结果 - 查看所有头像URL
SELECT id, username, 
       CASE 
           WHEN avatar LIKE 'https://yjwkusxabeto.sealoshzh.site%' THEN '✅ 正确'
           WHEN avatar LIKE 'https://hrhpdkpuwpxz.sealoshzh.site%' THEN '❌ 测试地址'
           WHEN avatar LIKE '/static/%' THEN '❌ 相对路径'
           ELSE '❓ 其他'
       END as url_status,
       avatar
FROM users
WHERE avatar IS NOT NULL
ORDER BY id;

-- 7. 测试头像URL是否可访问（需要复制URL到浏览器测试）
-- 示例：https://yjwkusxabeto.sealoshzh.site/static/avatars/2_15dbea36.jpg


