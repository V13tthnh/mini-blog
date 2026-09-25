import os
import shutil
from fastapi import UploadFile
from config import UPLOAD_DIR
from app.utils.sanitize import is_safe_file_extension, secure_filename

def save_uploaded_file(file: UploadFile | None, mode: str) -> tuple[bool, str | None, str | None]:

    if not file or not file.filename:
        return True, None, None

    if mode == "patched":
        # Patched Mode: Enforce extension whitelist and max size limit (5MB)
        if not is_safe_file_extension(file.filename):
            return False, "File tải lên không hợp lệ hoặc không được hệ thống hỗ trợ!", "upload_error"
        
        # Check size if available
        if file.size and file.size > 5 * 1024 * 1024:
            return False, "Kích thước file vượt quá giới hạn tối đa cho phép (5MB)!", "upload_error"

        safe_name = secure_filename(file.filename)
    else:
        # Vulnerable Mode: Unrestricted File Upload - Accepts any file extension (.html, .txt, .sh, .py, etc.)
        safe_name = file.filename

    save_path = os.path.join(UPLOAD_DIR, safe_name)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return True, f"/static/uploads/{safe_name}", None