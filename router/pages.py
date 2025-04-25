from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from main import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@router.get("/to_main", response_class=HTMLResponse)
async def welcome(request: Request, name: str):
    return templates.TemplateResponse("main_page.html", {"request": request, "name": name})