from fastapi import APIRouter, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from websocket.manager import manager
from main import templates
import random
router = APIRouter()

@router.get("/game", response_class=HTMLResponse)
async def enter_root(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})

@router.post("/choose_player")
async def select_player(player: int = Form(...)):
    if player not in [1, 2]:
        return RedirectResponse("/", status_code=303)
    return RedirectResponse(f"/game/{player}", status_code=303)

@router.get("/game/{player_id}", response_class=HTMLResponse)
async def game_page(request: Request, player_id: int):
    if player_id == 1:
        return templates.TemplateResponse(
            "player_1.html", 
            {
                "request": request,
                "season": manager.get_season(),
                "product": manager.get_product()
            }
        )
    else:
        return templates.TemplateResponse(
            "player_2.html", 
            {
                "request": request,
                "season": manager.get_season(),
                "product": manager.get_product()
            }
        )
    
@router.websocket("/ws/{player_id}")
async def websocket_endpoint(websocket: WebSocket, player_id: int):
    await manager.connect(player_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if player_id == 1:
                other_player = 2
            else:
                other_player = 1
            await manager.send_to_player(data, other_player)
    except WebSocketDisconnect:
        manager.disconnect(player_id)



    
    
    
    