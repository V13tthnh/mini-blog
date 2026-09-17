from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.utils.security import get_current_user
from app.services.admin_service import AdminService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def require_admin(request: Request):
    user = get_current_user(request)
    if not user or user.get("role") != "admin":
        return None
    return user

@router.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request, msg: str | None = None):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    data = AdminService.get_dashboard_data()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "current_user": user,
            "users": data["users"],
            "posts": data["posts"],
            "categories": data["categories"],
            "tags": data["tags"],
            "msg": msg,
            "mode": request.app.state.mode,
            "show_demo_notes": getattr(request.app.state, "show_demo_notes", False)
        }
    )

@router.get("/admin/toggle-mode")
def toggle_mode_admin(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    request.app.state.mode = "patched" if request.app.state.mode == "vulnerable" else "vulnerable"
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/admin/toggle-notes")
def toggle_notes_admin(request: Request):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    current_val = getattr(request.app.state, "show_demo_notes", False)
    request.app.state.show_demo_notes = not current_val
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/user/{target_user_id}/toggle-role")
def toggle_user_role(request: Request, target_user_id: int):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.toggle_user_role(target_user_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/user/{target_user_id}/edit")
def edit_user_by_admin(
    request: Request,
    target_user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    role: str = Form(...)
):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.edit_user(target_user_id, username, email, role)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/category/add")
def add_category(request: Request, name: str = Form(...), slug: str = Form("")):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.add_category(name, slug)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/category/edit/{cat_id}")
def edit_category(request: Request, cat_id: int, name: str = Form(...), slug: str = Form("")):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.edit_category(cat_id, name, slug)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/admin/category/delete/{cat_id}")
def delete_category(request: Request, cat_id: int):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.delete_category(cat_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/tag/add")
def add_tag(request: Request, name: str = Form(...), slug: str = Form("")):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.add_tag(name, slug)
    return RedirectResponse(url="/admin", status_code=303)

@router.post("/admin/tag/edit/{tag_id}")
def edit_tag(request: Request, tag_id: int, name: str = Form(...), slug: str = Form("")):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.edit_tag(tag_id, name, slug)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/admin/tag/delete/{tag_id}")
def delete_tag(request: Request, tag_id: int):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.delete_tag(tag_id)
    return RedirectResponse(url="/admin", status_code=303)

@router.get("/admin/post/delete/{post_id}")
def delete_post_admin(request: Request, post_id: int):
    user = require_admin(request)
    if not user:
        return RedirectResponse(url="/", status_code=303)

    AdminService.delete_post(post_id)
    return RedirectResponse(url="/admin", status_code=303)
