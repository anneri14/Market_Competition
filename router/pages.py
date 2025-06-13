from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app import templates

router = APIRouter() # Создаем роутер для группировки связанных маршрутов

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Обработчик GET-запросов, возвращает HTML-страницу landing.html"""
    return templates.TemplateResponse("landing.html", {"request": request})

@router.get("/to_main", response_class=HTMLResponse)
async def welcome(request: Request, name: str):
    """Обработчик GET-запросов, возвращает HTML-страницу main_page.html"""
    return templates.TemplateResponse("main_page.html", {"request": request, "name": name})

@router.get("/win_page", response_class=HTMLResponse)
async def win_page(request: Request):
    """Обработчик GET-запросов, возвращает HTML-страницу win_page.html"""
    return templates.TemplateResponse("win_page.html", {"request": request})

@router.get("/fail_page", response_class=HTMLResponse)
async def fail_page(request: Request):
    """Обработчик GET-запросов, возвращает HTML-страницу fail_page.html"""
    return templates.TemplateResponse("fail_page.html", {"request": request})

@router.get("/draw_page", response_class=HTMLResponse)
async def draw_page(request: Request):
    """Обработчик GET-запросов, возвращает HTML-страницу draw_page.html"""
    return templates.TemplateResponse("draw_page.html", {"request": request})