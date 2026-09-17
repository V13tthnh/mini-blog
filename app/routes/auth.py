from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from config import COOKIE_NAME
from app.utils.security import get_current_user
from app.services.auth_service import AuthService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    
    mode = request.app.state.mode
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "current_user": user,
            "mode": mode
        }
    )

@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    mode = request.app.state.mode
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    success, result, err_type = AuthService.process_login(client_ip, email, password, mode)
    if not success:
        status = 429 if err_type == "rate_limit" else 401
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "current_user": None,
                "mode": mode,
                "msg": result,
                "msg_type": "error"
            },
            status_code=status
        )

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key=COOKIE_NAME, value=result, httponly=True)
    return response

@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    
    mode = request.app.state.mode
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "current_user": user,
            "mode": mode
        }
    )

@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    mode = request.app.state.mode

    success, err_msg = AuthService.process_register(email, password, confirm_password)
    if not success:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "current_user": None,
                "mode": mode,
                "msg": err_msg,
                "msg_type": "error"
            },
            status_code=400
        )

    return RedirectResponse(url="/login?registered=1", status_code=303)

@router.get("/logout")
def logout(response: Response):
    res = RedirectResponse(url="/login", status_code=303)
    res.delete_cookie(COOKIE_NAME)
    return res
