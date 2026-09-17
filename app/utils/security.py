import hashlib
from itsdangerous import URLSafeTimedSerializer, BadSignature
from fastapi import Request
from config import SECRET_KEY, COOKIE_NAME
from database import get_db

serializer = URLSafeTimedSerializer(SECRET_KEY)

def hash_password(password: str) -> str:
    """Băm mật khẩu bằng SHA-256 kèm Salt an toàn"""
    salted = f"{SECRET_KEY}:{password}"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()

def verify_password(plain_password: str, stored_password: str) -> bool:
    """Xác thực mật khẩu (hỗ trợ cả mật khẩu băm SHA-256 và mật khẩu mẫu)"""
    if plain_password == stored_password:
        return True
    return hash_password(plain_password) == stored_password

def create_session_token(user_data: dict) -> str:
    """Tạo token mã hóa chứa thông tin user trong session cookie"""
    return serializer.dumps(user_data)

def decode_session_token(token: str) -> dict | None:
    """Giải mã token session cookie"""
    try:
        data = serializer.loads(token, max_age=86400 * 7) # Hạn dùng: 7 ngày
        return data
    except (BadSignature, Exception):
        return None

def get_current_user(request: Request) -> dict | None:
    """Dependency lấy thông tin user đăng nhập từ cookie"""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    
    session_data = decode_session_token(token)
    if not session_data or "user_id" not in session_data:
        return None
    
    conn = get_db()
    user = conn.execute("SELECT id, username, role, avatar_url, bio FROM users WHERE id = ?", (session_data["user_id"],)).fetchone()
    conn.close()
    
    return dict(user) if user else None

def generate_csrf_token(session_user_id: int) -> str:
    """Tạo CSRF token gắn với user ID"""
    return serializer.dumps({"csrf_for": session_user_id, "salt": "csrf"})

def verify_csrf_token(token: str, session_user_id: int) -> bool:
    """Xác thực CSRF token gửi lên từ Form"""
    if not token:
        return False
    try:
        data = serializer.loads(token, max_age=3600)
        return data.get("csrf_for") == session_user_id
    except Exception:
        return False
