-- Drop existing tables
DROP TABLE IF EXISTS post_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS comments;
DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    avatar_url TEXT DEFAULT '/static/uploads/default-avatar.svg',
    bio TEXT DEFAULT 'Thành viên Mini Blog ANM',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories table
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

-- Posts table
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER DEFAULT 1,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    image_url TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
);

-- Comments table
CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Tags table
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL
);

-- Post Tags junction table
CREATE TABLE post_tags (
    post_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (post_id, tag_id),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- Seed Data (Users, Categories, Tags, Posts, Comments)
INSERT INTO users (id, username, email, password, role, bio) VALUES
(1, 'admin', 'admin@example.com', 'admin123', 'admin', 'Quản trị viên hệ thống an ninh mạng'),
(2, 'alice', 'alice@example.com', 'alice123', 'user', 'Chuyên gia phân tích lỗ hổng web'),
(3, 'bob', 'bob@example.com', 'bob123', 'user', 'Lập trình viên thử nghiệm Pentest');

INSERT INTO categories (id, name, slug) VALUES
(1, 'Bảo Mật Web', 'bao-mat-web'),
(2, 'Kiểm Thử Xâm Nhập', 'kiem-thu-xam-nhap'),
(3, 'Lập Trình FastAPI', 'lap-trinh-fastapi'),
(4, 'Hệ Thống & CSDL', 'he-thong-csdl');

INSERT INTO tags (id, name, slug) VALUES
(1, 'OWASP', 'owasp'),
(2, 'SQLi', 'sqli'),
(3, 'XSS', 'xss'),
(4, 'Pentest', 'pentest'),
(5, 'CSRF', 'csrf'),
(6, 'IDOR', 'idor');

INSERT INTO posts (id, user_id, category_id, title, content) VALUES
(1, 1, 1, 'Chào mừng đến với Web Mini Blog ANM', 'Đây là ứng dụng Web Mini Blog thử nghiệm bảo mật. Hệ thống được tích hợp 6 lỗ hổng phổ biến theo OWASP Top 10 phục vụ việc kiểm thử xâm nhập (Pentest) và khắc phục (Patched).'),
(2, 2, 2, 'Tìm hiểu lỗ hổng SQL Injection và Stored XSS', 'SQL Injection cho phép kẻ tấn công chèn câu lệnh SQL trái phép. Stored XSS cho phép thực thi mã JavaScript độc hại lưu trong CSDL.');

INSERT INTO post_tags (post_id, tag_id) VALUES
(1, 1), (1, 4),
(2, 1), (2, 2), (2, 3);

INSERT INTO comments (id, post_id, user_id, content) VALUES
(1, 1, 2, 'Dự án rất trực quan và hữu ích!'),
(2, 1, 3, 'Rất mong chờ bài báo cáo hoàn chỉnh.');
