import random
from fastapi import APIRouter, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from websocket.manager import manager
from main import templates

router = APIRouter()

@router.get("/game", response_class=HTMLResponse)
async def enter_root(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})

@router.post("/create_game")
async def create_game(request: Request):
    game_id = manager.create_game_id()
    return templates.TemplateResponse("main_page.html", {"request": request, "game_id": game_id})

@router.post("/join_game")
async def join_game(request: Request, game_id: str = Form(...)):
    player_id = manager.join_game(game_id)
    if player_id == 0:
        return RedirectResponse("/join_game?error=invalid", status_code=303)
    if player_id == 1:
        if player_id in manager.games[game_id]:
            player_id = 2
            manager.games[game_id].append(2)
        else:
            manager.games[game_id].append(1)
    return RedirectResponse(f"/game/{game_id}/{player_id}", status_code=303)


@router.get("/game/{game_id}/{player_id}", response_class=HTMLResponse)
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

        await manager.send_round_result(best_player)

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

