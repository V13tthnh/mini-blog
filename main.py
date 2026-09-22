import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager

from database import init_db
from app.routes import auth, posts, profile, admin, files

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Mini Blog ANM - Pentest & Patched Demo",
    description="Ứng dụng thử nghiệm kiểm thử xâm nhập 6 lỗ hổng OWASP Top 10",
    version="1.0.0",
    lifespan=lifespan
)

# Chế độ ứng dụng: 'vulnerable' hoặc 'patched' (Mặc định: vulnerable)
app.state.mode = os.getenv("APP_MODE", "vulnerable").lower()
# Cấu hình ẩn/hiển thị ghi chú Pentest & Nút Chế độ trên giao diện (Mặc định: Ẩn)
app.state.show_demo_notes = False

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    mode = getattr(request.app.state, "mode", "vulnerable")
    if mode == "patched":
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com https://fonts.googleapis.com https://cdn.ckeditor.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.ckeditor.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.ckeditor.com; "
            "img-src 'self' data: https:;"
        )
    return response

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(profile.router)
app.include_router(admin.router)
app.include_router(files.router)

@app.get("/toggle-mode")
def toggle_mode(request: Request):
    if app.state.mode == "vulnerable":
        app.state.mode = "patched"
    else:
        app.state.mode = "vulnerable"
    
    referrer = request.headers.get("referer", "/")
    return RedirectResponse(url=referrer, status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)