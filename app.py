from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI() #создание экземпляра FastAPI приложения

templates = Jinja2Templates(directory="templates") #инициализация шаблонов Jinja2
app.mount("/static", StaticFiles(directory="static"), name="static") #монтирование статических файлов

from router import authentication, game, pages

#подключение роутеров к основному приложению
app.include_router(pages.router)
app.include_router(authentication.router)
app.include_router(game.router)

#настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
