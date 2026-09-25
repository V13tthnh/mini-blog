import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from config import PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASSWORD, PG_SUPER_USER, PG_SUPER_PASSWORD

def init_postgres():
    print("[PostgreSQL Setup] Step 1: Connecting as Superuser to create Database and App User...")
    # Connect to default postgres DB as superuser
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname="postgres",
        user=PG_SUPER_USER,
        password=PG_SUPER_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Create Database if not exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (PG_DB,))
    if not cursor.fetchone():
        print(f"[PostgreSQL Setup] Creating database '{PG_DB}'...")
        cursor.execute(f"CREATE DATABASE {PG_DB}")
    else:
        print(f"[PostgreSQL Setup] Database '{PG_DB}' already exists.")

    # Create App User if not exists
    cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (PG_USER,))
    if not cursor.fetchone():
        print(f"[PostgreSQL Setup] Creating Least Privilege App User '{PG_USER}'...")
        cursor.execute(f"CREATE USER {PG_USER} WITH PASSWORD %s", (PG_PASSWORD,))
    else:
        print(f"[PostgreSQL Setup] Least Privilege App User '{PG_USER}' already exists. Updating password...")
        cursor.execute(f"ALTER USER {PG_USER} WITH PASSWORD %s", (PG_PASSWORD,))

    cursor.close()
    conn.close()

    print("[PostgreSQL Setup] Step 2: Connecting to 'miniblog_db' to initialize schema and grants...")
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_SUPER_USER,
        password=PG_SUPER_PASSWORD
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    # Drop existing tables to ensure clean state
    schema_script = """
    DROP TABLE IF EXISTS post_tags CASCADE;
    DROP TABLE IF EXISTS tags CASCADE;
    DROP TABLE IF EXISTS comments CASCADE;
    DROP TABLE IF EXISTS posts CASCADE;
    DROP TABLE IF EXISTS categories CASCADE;
    DROP TABLE IF EXISTS users CASCADE;

    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE,
        password VARCHAR(255) NOT NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'user',
        avatar_url VARCHAR(500) DEFAULT '/static/uploads/default-avatar.svg',
        bio TEXT DEFAULT 'Thành viên Mini Blog ANM',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE categories (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        slug VARCHAR(255) UNIQUE NOT NULL
    );

    CREATE TABLE posts (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        category_id INTEGER DEFAULT 1 REFERENCES categories(id) ON DELETE SET NULL,
        title VARCHAR(500) NOT NULL,
        content TEXT NOT NULL,
        image_url VARCHAR(500) DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE comments (
        id SERIAL PRIMARY KEY,
        post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE tags (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) UNIQUE NOT NULL,
        slug VARCHAR(255) UNIQUE NOT NULL
    );

    CREATE TABLE post_tags (
        post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
        tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
        PRIMARY KEY (post_id, tag_id)
    );

    -- Seed Initial Data
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

    -- Reset sequences for SERIAL columns
    SELECT setval(pg_get_serial_sequence('users', 'id'), coalesce(max(id), 1)) FROM users;
    SELECT setval(pg_get_serial_sequence('categories', 'id'), coalesce(max(id), 1)) FROM categories;
    SELECT setval(pg_get_serial_sequence('tags', 'id'), coalesce(max(id), 1)) FROM tags;
    SELECT setval(pg_get_serial_sequence('posts', 'id'), coalesce(max(id), 1)) FROM posts;
    SELECT setval(pg_get_serial_sequence('comments', 'id'), coalesce(max(id), 1)) FROM comments;

    -- Grant Least Privilege permissions to miniblog_app_user
    GRANT CONNECT ON DATABASE miniblog_db TO miniblog_app_user;
    GRANT USAGE ON SCHEMA public TO miniblog_app_user;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO miniblog_app_user;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO miniblog_app_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO miniblog_app_user;
    """

    cursor.execute(schema_script)
    print("[PostgreSQL Setup] Step 3: Schema created and Least Privilege permissions granted successfully!")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    init_postgres()
