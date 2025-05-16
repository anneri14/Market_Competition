import random
from fastapi import APIRouter, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from websocket.manager import manager
from main import templates

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

@router.post("/submit_price_quality")
async def submit_price_quality(request: Request, player_id: int = Form(...), price: int = Form(...), quality: str = Form(...)):
    round_num = manager.cur_round

    if round_num not in manager.player_data:
        manager.player_data[round_num] = {}
        
    manager.player_data[round_num][player_id] = {
        "price": price,
        "quality": quality
    }

    best_player = None

    if len(manager.player_data[round_num]) == 2:
        p1 = manager.player_data[round_num][1]
        p2 = manager.player_data[round_num][2]

        if p1["price"] < p2["price"]:
            best_player = 1
        elif p1["price"] > p2["price"]:
            best_player = 2
        else:
            best_player = random.choice([1, 2])

        if best_player is not None:
            for pid in [1, 2]:
                if pid in manager.active_connections:
                    await manager.send_to_player(f"Лучший игрок: Игрок {best_player}", pid)

    return {"success": True}


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

