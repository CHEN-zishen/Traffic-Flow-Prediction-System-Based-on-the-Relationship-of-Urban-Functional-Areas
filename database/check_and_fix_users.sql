-- 检查并修复users表
-- 此脚本会保留现有数据（如果有的话）

-- 1. 检查表是否存在
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN '表已存在'
        ELSE '表不存在'
    END AS table_status
FROM information_schema.tables 
WHERE table_schema = 'traffic_db' 
AND table_name = 'users';

-- 2. 如果表存在，检查字段
SELECT 
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'traffic_db'
AND TABLE_NAME = 'users'
ORDER BY ORDINAL_POSITION;

-- 3. 备份现有数据（如果表存在）
-- 注意：下面的语句需要根据实际情况手动执行
-- CREATE TABLE users_backup AS SELECT * FROM users;

-- 4. 添加缺失的字段（如果表已存在但字段不全）
-- ALTER TABLE `users` ADD COLUMN `nickname` VARCHAR(50) DEFAULT NULL COMMENT '昵称' AFTER `password_hash`;
-- ALTER TABLE `users` ADD COLUMN `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL' AFTER `nickname`;
-- ALTER TABLE `users` ADD COLUMN `role` VARCHAR(20) DEFAULT 'user' COMMENT '角色：admin/user' AFTER `avatar`;
-- ALTER TABLE `users` ADD COLUMN `last_login_time` DATETIME DEFAULT NULL COMMENT '最后登录时间' AFTER `status`;
-- ALTER TABLE `users` ADD COLUMN `last_login_ip` VARCHAR(50) DEFAULT NULL COMMENT '最后登录IP' AFTER `last_login_time`;
-- ALTER TABLE `users` ADD COLUMN `login_count` INT DEFAULT 0 COMMENT '登录次数' AFTER `last_login_ip`;

