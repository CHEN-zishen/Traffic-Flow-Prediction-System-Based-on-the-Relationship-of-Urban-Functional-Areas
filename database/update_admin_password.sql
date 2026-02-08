-- 更新管理员密码
-- 将admin用户的密码设置为: admin123

USE traffic_db;

-- 更新密码哈希为正确的值
UPDATE users 
SET password_hash = '$2b$12$8cGK2oVISHD0kGZwNkLa3.pkxCT4yzk.nUX/w/mfUVpWFF0tLSU7W',
    nickname = '系统管理员',
    role = 'admin',
    status = 1
WHERE username = 'admin';

-- 如果admin用户不存在，则插入
INSERT INTO users (username, email, password_hash, nickname, role, status)
SELECT 'admin', 'admin@traffic.com', '$2b$12$8cGK2oVISHD0kGZwNkLa3.pkxCT4yzk.nUX/w/mfUVpWFF0tLSU7W', '系统管理员', 'admin', 1
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- 查看结果
SELECT username, email, nickname, role, status, created_at 
FROM users 
WHERE username = 'admin';

