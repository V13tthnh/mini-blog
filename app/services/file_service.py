import os
from fastapi import Response
from fastapi.responses import FileResponse, PlainTextResponse
from config import BASE_DIR, UPLOAD_DIR

class FileService:
    @staticmethod
    def read_file(file_param: str, mode: str) -> Response:
        """
        Reads and serves a file based on file_param.
        - vulnerable mode: Allows path traversal via `../` (e.g., file=../../schema.sql or file=../../config.py)
        - patched mode: Restricts file path to UPLOAD_DIR using os.path.basename & canonical path check.
        """
        if not file_param:
            return PlainTextResponse("Missing 'file' parameter", status_code=400)

        if mode == "vulnerable":
            # Vulnerable: Unsanitized path join allows directory traversal
            target_path = os.path.normpath(os.path.join(UPLOAD_DIR, file_param))
        else:
            # Patched: Chặn hoàn toàn ký tự đường dẫn duyệt thư mục (../, \, /) và xác minh canonical path
            if ".." in file_param or "/" in file_param or "\\" in file_param or os.path.basename(file_param) != file_param:
                return PlainTextResponse("Access Denied: Path Traversal Attempt Detected (HTTP 403 Forbidden)", status_code=403)

            safe_name = os.path.basename(file_param)
            target_path = os.path.realpath(os.path.join(UPLOAD_DIR, safe_name))
            real_upload_dir = os.path.realpath(UPLOAD_DIR)

            if not target_path.startswith(real_upload_dir):
                return PlainTextResponse("Access Denied: Path Traversal Attempt Detected (HTTP 403 Forbidden)", status_code=403)

        if not os.path.exists(target_path) or not os.path.isfile(target_path):
            return PlainTextResponse(f"File not found: {file_param}", status_code=404)

        try:
            # Return plain text for code/sql/config files, FileResponse for media
            ext = os.path.splitext(target_path)[1].lower()
            if ext in [".txt", ".sql", ".py", ".md", ".json", ".log", ".env", ".css", ".js", ".html"]:
                with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                return PlainTextResponse(content)
            return FileResponse(target_path)
        except Exception as e:
            return PlainTextResponse(f"Error reading file: {e}", status_code=500)
