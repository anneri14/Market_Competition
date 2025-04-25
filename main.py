from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

from router import authentication, game, pages

app.include_router(pages.router)
app.include_router(authentication.router)
app.include_router(game.router)
