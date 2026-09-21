from fastapi import APIRouter, Request
from app.services.file_service import FileService

router = APIRouter()

@router.get("/file/view")
def view_file_route(request: Request, file: str = ""):
    mode = request.app.state.mode
    return FileService.read_file(file, mode)
