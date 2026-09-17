from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.utils.security import get_current_user, generate_csrf_token
from app.services.post_service import PostService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def home_page(request: Request, cat: str | None = None, tag: str | None = None):
    user = get_current_user(request)
    mode = request.app.state.mode
    show_demo_notes = getattr(request.app.state, "show_demo_notes", False)

    data = PostService.get_home_data(cat, tag)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request=request,
            name="partials/post_list.html",
            context={"posts": data["posts"], "show_demo_notes": show_demo_notes}
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_user": user,
            "posts": data["posts"],
            "recommended_posts": data["recommended_posts"],
            "categories": data["categories"],
            "all_tags": data["all_tags"],
            "current_cat": cat,
            "current_tag": tag,
            "mode": mode,
            "show_demo_notes": show_demo_notes
        }
    )

@router.get("/search", response_class=HTMLResponse)
def search_posts(request: Request, q: str = ""):
    user = get_current_user(request)
    mode = request.app.state.mode
    show_demo_notes = getattr(request.app.state, "show_demo_notes", False)

    data = PostService.search_posts(q, mode)

    if request.headers.get("HX-Request"):
        return templates.TemplateResponse(
            request=request,
            name="partials/post_list.html",
            context={"posts": data["posts"], "show_demo_notes": show_demo_notes}
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "current_user": user,
            "posts": data["posts"],
            "recommended_posts": data["recommended_posts"],
            "categories": data["categories"],
            "all_tags": data["all_tags"],
            "query": q,
            "mode": mode,
            "show_demo_notes": show_demo_notes
        }
    )

@router.get("/post/create", response_class=HTMLResponse)
def create_post_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    mode = request.app.state.mode
    show_demo_notes = getattr(request.app.state, "show_demo_notes", False)
    categories = PostService.get_categories()
    csrf_token = generate_csrf_token(user["id"]) if mode == "patched" else ""

    return templates.TemplateResponse(
        request=request,
        name="create_post.html",
        context={
            "current_user": user,
            "categories": categories,
            "csrf_token": csrf_token,
            "mode": mode,
            "show_demo_notes": show_demo_notes
        }
    )

@router.post("/post/create")
async def create_post_submit(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    category_id: int = Form(1),
    tags_input: str = Form(""),
    csrf_token: str = Form(""),
    image: UploadFile | None = File(None)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    mode = request.app.state.mode
    show_demo_notes = getattr(request.app.state, "show_demo_notes", False)

    success, err_context, status_code = PostService.create_post(
        user=user,
        title=title,
        content=content,
        category_id=category_id,
        tags_input=tags_input,
        csrf_token=csrf_token,
        image=image,
        mode=mode
    )

    if not success:
        err_dict = err_context or {}
        return templates.TemplateResponse(
            request=request,
            name="create_post.html",
            context={
                "current_user": user,
                "mode": mode,
                "show_demo_notes": show_demo_notes,
                **err_dict
            },
            status_code=status_code
        )

    return RedirectResponse(url="/", status_code=303)

@router.get("/post/{post_id}", response_class=HTMLResponse)
def post_detail(request: Request, post_id: int):
    user = get_current_user(request)
    mode = request.app.state.mode
    show_demo_notes = getattr(request.app.state, "show_demo_notes", False)

    post, comments = PostService.get_post_detail(post_id)
    if not post:
        return RedirectResponse(url="/", status_code=303)

    csrf_token = generate_csrf_token(user["id"]) if (user and mode == "patched") else ""

    return templates.TemplateResponse(
        request=request,
        name="post_detail.html",
        context={
            "current_user": user,
            "post": post,
            "comments": comments,
            "csrf_token": csrf_token,
            "mode": mode,
            "show_demo_notes": show_demo_notes
        }
    )

@router.post("/post/{post_id}/comment")
def add_comment(
    request: Request,
    post_id: int,
    content: str = Form(...),
    csrf_token: str = Form("")
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    mode = request.app.state.mode
    show_demo_notes = getattr(request.app.state, "show_demo_notes", False)

    success, err_type, post, comments = PostService.add_comment(user, post_id, content, csrf_token, mode)
    if not success:
        return RedirectResponse(url=f"/post/{post_id}?error={err_type}", status_code=303)

    if request.headers.get("HX-Request"):
        new_csrf_token = generate_csrf_token(user["id"]) if mode == "patched" else ""
        return templates.TemplateResponse(
            request=request,
            name="partials/comment_section.html",
            context={
                "current_user": user,
                "post": post,
                "comments": comments,
                "csrf_token": new_csrf_token,
                "mode": mode,
                "show_demo_notes": show_demo_notes
            }
        )

    return RedirectResponse(url=f"/post/{post_id}", status_code=303)

@router.get("/post/edit/{post_id}", response_class=HTMLResponse)
def edit_post_page(request: Request, post_id: int):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    mode = request.app.state.mode
    show_demo_notes = getattr(request.app.state, "show_demo_notes", False)

    success, post, categories, tags_str = PostService.get_edit_post_data(user, post_id)
    if not success:
        return RedirectResponse(url=f"/post/{post_id}" if post else "/", status_code=303)

    csrf_token = generate_csrf_token(user["id"]) if mode == "patched" else ""

    return templates.TemplateResponse(
        request=request,
        name="edit_post.html",
        context={
            "current_user": user,
            "post": post,
            "categories": categories,
            "tags_str": tags_str,
            "csrf_token": csrf_token,
            "mode": mode,
            "show_demo_notes": show_demo_notes
        }
    )

@router.post("/post/edit/{post_id}")
async def edit_post_submit(
    request: Request,
    post_id: int,
    title: str = Form(...),
    content: str = Form(...),
    category_id: int = Form(1),
    tags_input: str = Form(""),
    csrf_token: str = Form(""),
    image: UploadFile | None = File(None)
):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    mode = request.app.state.mode
    show_demo_notes = getattr(request.app.state, "show_demo_notes", False)

    success, err_context, status_code = PostService.edit_post(
        user=user,
        post_id=post_id,
        title=title,
        content=content,
        category_id=category_id,
        tags_input=tags_input,
        csrf_token=csrf_token,
        image=image,
        mode=mode
    )

    if not success:
        if err_context and "redirect" in err_context:
            return RedirectResponse(url=err_context["redirect"], status_code=303)
        err_dict = err_context or {}
        return templates.TemplateResponse(
            request=request,
            name="edit_post.html",
            context={
                "current_user": user,
                "mode": mode,
                "show_demo_notes": show_demo_notes,
                **err_dict
            },
            status_code=status_code
        )

    return RedirectResponse(url=f"/post/{post_id}", status_code=303)
