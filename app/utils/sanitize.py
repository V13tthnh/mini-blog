import bleach
import re
import os

# Whitelist các thẻ HTML và thuộc tính an toàn cho bài viết
ALLOWED_TAGS = ['p', 'b', 'i', 'u', 'em', 'strong', 'a', 'h1', 'h2', 'h3', 'code', 'pre', 'ul', 'ol', 'li', 'blockquote']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title']
}
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

def clean_html(text: str) -> str:
    """Lọc các thẻ HTML/JS độc hại (Vá lỗi Stored XSS)"""
    if not text:
        return ""
    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def is_safe_file_extension(filename: str) -> bool:
    """Kiểm tra định dạng đuôi file cho phép"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def secure_filename(filename: str) -> str:
    """Loại bỏ ký tự đặc biệt và đường dẫn độc hại (Vá lỗi Path Traversal)"""
    filename = os.path.basename(filename)
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '_', filename)
    return filename
