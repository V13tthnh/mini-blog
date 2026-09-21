import time
from database import get_db
from app.utils.security import create_session_token, hash_password, verify_password

LOGIN_ATTEMPTS: dict[str, dict] = {}

class AuthService:
    @staticmethod
    def process_login(client_ip: str, email: str, password: str, mode: str) -> tuple[bool, str, str | None]:
        """
        Processes user login logic.
        Returns (success, token_or_error_msg, error_type_if_failed).
        """
        now = time.time()

        if mode == "patched":
            attempt = LOGIN_ATTEMPTS.get(client_ip, {"count": 0, "reset_time": now + 60})
            if now > attempt["reset_time"]:
                attempt = {"count": 0, "reset_time": now + 60}

            if attempt["count"] >= 5:
                return False, "Lỗi 429 Too Many Requests: Đăng nhập sai quá 5 lần. Vui lòng thử lại sau 1 phút!", "rate_limit"

        conn = get_db()
        email_clean = email.strip()

        if mode == "vulnerable":
            # Pure SQL concatenation vulnerability:
            # Payload `' OR 1=1 --` turns query into:
            # SELECT * FROM users WHERE email = '' OR 1=1 --' OR username = '...'
            raw_sql = f"SELECT * FROM users WHERE email = '{email}' OR username = '{email}'"
            print(f"[SQLi Login Debug]: {raw_sql}")
            try:
                user_raw = conn.execute(raw_sql).fetchone()
            except Exception as e:
                print(f"[SQLi Login Error Demo]: {e}")
                user_raw = None
            conn.close()

            if not user_raw:
                return False, "Mật khẩu hoặc Email đăng nhập không chính xác!", "invalid_credentials"

            user = dict(user_raw)
            token = create_session_token({"user_id": user["id"], "username": user["username"], "role": user["role"]})
            return True, token, None

        user = conn.execute("SELECT * FROM users WHERE email = ? OR username = ?", (email_clean, email_clean)).fetchone()
        conn.close()

        if not user or not verify_password(password, user["password"]):
            if mode == "patched":
                attempt = LOGIN_ATTEMPTS.get(client_ip, {"count": 0, "reset_time": now + 60})
                attempt["count"] += 1
                LOGIN_ATTEMPTS[client_ip] = attempt

            return False, "Mật khẩu hoặc Email đăng nhập không chính xác!", "invalid_credentials"

        if client_ip in LOGIN_ATTEMPTS:
            del LOGIN_ATTEMPTS[client_ip]

        token = create_session_token({"user_id": user["id"], "username": user["username"], "role": user["role"]})
        return True, token, None

    @staticmethod
    def process_register(email: str, password: str, confirm_password: str) -> tuple[bool, str | None]:
        """
        Processes user registration logic.
        Returns (success, error_msg_if_failed).
        """
        if password != confirm_password:
            return False, "Mật khẩu xác nhận không khớp!"

        email_clean = email.strip()
        username_derived = email_clean.split("@")[0]

        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email_clean, username_derived)).fetchone()
        if existing:
            conn.close()
            return False, "Địa chỉ Email này đã được đăng ký!"

        hashed_pw = hash_password(password)
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username_derived, email_clean, hashed_pw)
        )
        conn.commit()
        conn.close()

        return True, None
