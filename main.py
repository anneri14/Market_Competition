from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
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

@app.get("/game", response_class=HTMLResponse)
async def enter_root(request: Request):

    return templates.TemplateResponse("/game.html", {"request": request})

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, player_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[player_id] = websocket
        print(f"Игрок {player_id} подключен")

    def disconnect(self, player_id: int):
        if player_id in self.active_connections:
            del self.active_connections[player_id]
            print(f"Игрок {player_id} отключен")

    async def send_to_player(self, message: str, player_id: int):
        if player_id in self.active_connections:
            await self.active_connections[player_id].send_text(message)

manager = ConnectionManager()


@app.post("/choose_player")
async def select_player(player: int = Form(...)):
    if player not in [1, 2]:
        return RedirectResponse("/", status_code=303)
    return RedirectResponse(f"/game/{player}", status_code=303)

@app.get("/game/{player_id}", response_class=HTMLResponse)
async def game_page(request: Request, player_id: int):
    if player_id == 1:
        return templates.TemplateResponse("player_1.html", {"request": request})
    else:
        return templates.TemplateResponse("player_2.html", {"request": request})

@app.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int):
    await manager.connect(player_id, websocket)
    try:
        while True:
            # Получаем действия от игрока
            data = await websocket.receive_text()
            print(f"Игрок {player_id} отправил: {data}")
            
            # Пересылаем действие другому игроку
            other_player = 2 if player_id == 1 else 1
            await manager.send_to_player(data, other_player)
            
    except WebSocketDisconnect:
        manager.disconnect(player_id)