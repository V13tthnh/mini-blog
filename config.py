import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
DB_PATH = os.path.join(STORAGE_DIR, "blog.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

SECRET_KEY = "anm_pentest_secret_key_2026"
COOKIE_NAME = "session_token"

# PostgreSQL Configuration (Least Privilege DB)
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB = os.getenv("PG_DB", "miniblog_db")
PG_USER = os.getenv("PG_USER", "miniblog_app_user")
PG_PASSWORD = os.getenv("PG_PASSWORD", "App_Secure_Password_2026!")
PG_SUPER_USER = os.getenv("PG_SUPER_USER", "postgres")
PG_SUPER_PASSWORD = os.getenv("PG_SUPER_PASSWORD", "onepiece2016")

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

