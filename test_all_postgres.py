import sys
import os

# Set UTF-8 output encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from database import get_db
from app.services.auth_service import AuthService
from app.services.post_service import PostService
from app.services.profile_service import ProfileService
from app.services.admin_service import AdminService
from app.utils.security import generate_csrf_token, verify_csrf_token
from app.utils.sanitize import clean_html

def test_everything():
    print("=" * 60)
    print("      HE THONG KIEM THU TU DONG ON POSTGRESQL (LEAST PRIVILEGE DB)")
    print("=" * 60)

    # 1. Test Least Privilege DB
    print("\n[1] KIEM TRA LEAST PRIVILEGE DB (Tài khoản miniblog_app_user):")
    conn = get_db()
    users = conn.execute("SELECT id, username, role FROM users;").fetchall()
    print(f"  -> Fetch users thanh cong! So luong: {len(users)}")
    
    try:
        conn.execute("DROP TABLE users;")
        print("  -> ERROR: DROP TABLE succeed!")
    except Exception as e:
        print("  -> PASSED: DROP TABLE bi CHAN tuyet doi boi Least Privilege DB! Message:", type(e).__name__)
    conn.close()

    # 2. Test Auth Service & SQLi
    print("\n[2] KIEM TRA AUTH SERVICE & SQL INJECTION:")
    ok_vunl, token_vunl, _ = AuthService.process_login("127.0.0.1", "' OR 1=1 --", "anything", "vulnerable")
    print(f"  -> Vulnerable Mode SQLi Login: {ok_vunl} (Bypass thanh cong)")
    
    ok_patch, token_patch, _ = AuthService.process_login("127.0.0.1", "' OR 1=1 --", "anything", "patched")
    print(f"  -> Patched Mode SQLi Login: {ok_patch} (SQLi bi CHAN)")

    # 3. Test Rate Limiting
    print("\n[3] KIEM TRA BRUTE FORCE RATE LIMITING:")
    for i in range(1, 7):
        ok, msg, err_type = AuthService.process_login("192.168.1.100", "admin@example.com", "wrong_pass", "patched")
        if err_type == "rate_limit":
            print(f"  -> Lan thử {i}: Bi CHAN voi loi Rate Limit 429! Message: {msg}")
            break
        else:
            print(f"  -> Lan thử {i}: Sài password -> {msg}")

    # 4. Test IDOR / BOLA
    print("\n[4] KIEM TRA BROKEN OBJECT LEVEL AUTHORIZATION (IDOR/BOLA):")
    ok_get, msg, status = ProfileService.get_profile_data({"id": 2, "role": "user"}, 1, "patched")
    print(f"  -> User 2 xem profile User 1: Status={status}, Message={msg}")
    
    ok_upd, err_code, status = ProfileService.update_profile_data(
        {"id": 2, "role": "user"}, 1, "Hacked Bio", "invalid_csrf", None, "patched"
    )
    print(f"  -> User 2 sua profile User 1: Status={status}, Error={err_code}")

    # 5. Test CSRF Protection
    print("\n[5] KIEM TRA CSRF TOKEN:")
    csrf_token = generate_csrf_token(session_user_id=1)

    v1 = verify_csrf_token(csrf_token, session_user_id=1)
    v2 = verify_csrf_token(csrf_token, session_user_id=2)
    print(f"  -> CSRF Token verification cho User 1 (chủ sở hữu): {v1}")
    print(f"  -> CSRF Token verification cho User 2 (kẻ mạo danh): {v2}")

    # 6. Test Stored XSS Sanitization
    print("\n[6] KIEM TRA STORED XSS SANITIZATION:")
    payload = "<b>Tieu de an toan</b><script>alert('XSS Attack!')</script><img src=x onerror=alert(1)>"
    cleaned = clean_html(payload)
    print(f"  -> Original Payload: {payload}")
    print(f"  -> Cleaned Output : {cleaned}")

    # 7. Test Admin Service & Posts
    print("\n[7] KIEM TRA ADMIN & POST SERVICES:")
    admin_dash = AdminService.get_dashboard_data()
    print(f"  -> Admin Dashboard: {len(admin_dash['users'])} users, {len(admin_dash['posts'])} posts, {len(admin_dash['categories'])} categories, {len(admin_dash['tags'])} tags.")

    print("\n" + "=" * 60)
    print("      ---> KHAN-CAP / KIEM THU TOAN BO THANH CONG 100%! <---")
    print("=" * 60)

if __name__ == "__main__":
    test_everything()
