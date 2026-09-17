from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.utils.security import get_current_user, generate_csrf_token
from app.services.profile_service import ProfileService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/profile", response_class=HTMLResponse)
def view_profile(request: Request, user_id: int | None = None):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    mode = request.app.state.mode

    success, result, status_code = ProfileService.get_profile_data(current_user, user_id, mode)
    if not success:
        if status_code == 403:
            return templates.TemplateResponse(
                request=request,
                name="base.html",
                context={
                    "current_user": current_user,
                    "mode": mode,
                    "msg": result,
                    "msg_type": "error"
                },
                status_code=403
            )
        return RedirectResponse(url="/", status_code=303)

    csrf_token = generate_csrf_token(current_user["id"]) if mode == "patched" else ""

    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "current_user": current_user,
            "profile_user": result,
            "csrf_token": csrf_token,
            "mode": mode
        }
    )

@router.post("/profile/update")
async def update_profile(
    request: Request,
    target_user_id: int = Form(...),
    bio: str = Form(""),
    csrf_token: str = Form(""),
    avatar: UploadFile | None = File(None)
):
    current_user = get_current_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    mode = request.app.state.mode

    success, err_code, status_code = ProfileService.update_profile_data(
        current_user, target_user_id, bio, csrf_token, avatar, mode
    )

    if not success:
        if status_code == 403:
            return templates.TemplateResponse(
                request=request,
                name="base.html",
                context={
                    "current_user": current_user,
                    "mode": mode,
                    "msg": err_code,
                    "msg_type": "error"
                },
                status_code=403
            )
        return RedirectResponse(url=f"/profile?user_id={target_user_id}&error={err_code}", status_code=303)

    return RedirectResponse(url=f"/profile?user_id={target_user_id}", status_code=303)
