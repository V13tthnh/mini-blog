import os
import shutil
from fastapi import UploadFile
from config import UPLOAD_DIR
from app.utils.sanitize import is_safe_file_extension, secure_filename

def save_uploaded_file(file: UploadFile | None, mode: str) -> tuple[bool, str | None, str | None]:
    """
    Saves an uploaded file to UPLOAD_DIR.
    Returns (success, image_url_or_error_msg, error_type).
    """
    if not file or not file.filename:
        return True, None, None

    if mode == "patched":
        # Patched Mode: Enforce extension whitelist and max size limit (5MB)
        if not is_safe_file_extension(file.filename):
            return False, "Lỗi File Upload 400: Chỉ cho phép định dạng ảnh an toàn (.jpg, .jpeg, .png, .gif, .webp)!", "file_type"
        
        # Check size if available
        if file.size and file.size > 5 * 1024 * 1024:
            return False, "Lỗi File Upload 400: Kích thước file vượt quá giới hạn tối đa (5MB)!", "file_size"

        safe_name = secure_filename(file.filename)
    else:
        # Vulnerable Mode: Unrestricted File Upload - Accepts any file extension (.html, .txt, .sh, .py, etc.)
        safe_name = file.filename

    save_path = os.path.join(UPLOAD_DIR, safe_name)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return True, f"/static/uploads/{safe_name}", None
