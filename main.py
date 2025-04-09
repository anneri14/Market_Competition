from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
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

@app.post("/submit_name")
async def submit_name(name: str = Form(...)):
    if not name.strip():
        return RedirectResponse("/", status_code=303)
    return RedirectResponse(f"/to_main?name={name}", status_code=303)

@app.get("/to_main", response_class=HTMLResponse)
async def welcome(request: Request, name: str):
    return templates.TemplateResponse("main_page.html", {
        "request": request,
        "name": name
    })

