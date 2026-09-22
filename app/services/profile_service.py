from fastapi import UploadFile
from database import get_db
from app.utils.security import generate_csrf_token, verify_csrf_token
from app.utils.file_upload import save_uploaded_file

class ProfileService:
    @staticmethod
    def get_profile_data(current_user: dict, target_user_id: int | None, mode: str) -> tuple[bool, dict | str, int]:

        target_id = target_user_id if target_user_id is not None else current_user["id"]

        if mode == "patched":
            if target_id != current_user["id"] and current_user["role"] != "admin":
                return False, "Lỗi 403 Forbidden: Bạn không có quyền truy cập hồ sơ của người dùng khác", 403

        conn = get_db()
        profile_user = conn.execute(
            "SELECT id, username, role, avatar_url, bio, created_at FROM users WHERE id = ?",
            (target_id,)
        ).fetchone()
        conn.close()

        if not profile_user:
            return False, "Không tìm thấy người dùng", 404

        return True, dict(profile_user), 200

    @staticmethod
    def update_profile_data(
        current_user: dict,
        target_user_id: int,
        bio: str,
        csrf_token: str,
        avatar: UploadFile | None,
        mode: str
    ) -> tuple[bool, str | None, int]:
        
        if mode == "patched":
            if target_user_id != current_user["id"] and current_user["role"] != "admin":
                return False, "Lỗi 403 Forbidden: Không thể chỉnh sửa hồ sơ người khác!", 403

            if not verify_csrf_token(csrf_token, current_user["id"]):
                return False, "csrf_error", 303

            from app.utils.sanitize import clean_html
            bio = clean_html(bio)

        upload_success, avatar_url, err_type = save_uploaded_file(avatar, mode)
        if not upload_success:
            return False, "file_type_error", 303

        conn = get_db()
        if avatar_url:
            conn.execute("UPDATE users SET bio = ?, avatar_url = ? WHERE id = ?", (bio, avatar_url, target_user_id))
        else:
            conn.execute("UPDATE users SET bio = ? WHERE id = ?", (bio, target_user_id))

        conn.commit()
        conn.close()

        return True, None, 200
