from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app import templates

router = APIRouter() # Создаем роутер для группировки связанных маршрутов

@router.get("/enter", response_class=HTMLResponse)
async def enter_root(request: Request):
    """Обработчик GET-запросов, возвращает HTML-страницу enter.html"""
    return templates.TemplateResponse("enter.html", {"request": request})

@router.post("/submit_name")
async def submit_name(name: str = Form(...)):
    """Обработчик POST-запросов, принимает имя из формы и перенаправляет пользователя"""
    if not name.strip():
        return RedirectResponse("/", status_code=303)
    return RedirectResponse(f"/to_main?name={name}", status_code=303)