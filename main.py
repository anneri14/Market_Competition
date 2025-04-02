from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/enter", response_class=HTMLResponse)
async def enter_root(request: Request):
    return templates.TemplateResponse("enter.html", {"request": request})

@app.get("/to_main", response_class=HTMLResponse)
async def main_root(request: Request):
    return templates.TemplateResponse("main_page.html", {"request": request})

