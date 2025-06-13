import random
from fastapi import APIRouter, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse
from websocket.manager import manager
from app import templates

router = APIRouter() # Создаем роутер для группировки связанных маршрутов

@router.get("/game", response_class=HTMLResponse)
async def enter_root(request: Request):
    """Обработчик GET-запросов, возвращает HTML-страницу game.html"""
    return templates.TemplateResponse("game.html", {"request": request})


@router.post("/create_game")
async def create_game(request: Request):
    """Обработчик POST-запросов, создание новой игры"""
    game_id = manager.create_game_id()
    return templates.TemplateResponse("main_page.html", {"request": request, "game_id": game_id})


@router.post("/join_game")
async def join_game(request: Request, game_id: str = Form(...)):
    """Обработчик POST-запросов, присоединение к существующей игре"""
    player_id = manager.join_game(game_id)
    if player_id == 0:
        return RedirectResponse("/join_game?error=invalid", status_code=303)
    
    return RedirectResponse(f"/game/{game_id}/{player_id}", status_code=303)


@router.get("/game/{game_id}/{player_id}", response_class=HTMLResponse)
async def game_page(request: Request, game_id: str, player_id: int):
    """Обработчик GET-запросов, отображение игрового интерфейса"""
    player_choices = manager.get_player_choices(game_id, player_id)

    if player_id == 1:
        opponent_id = 2
    else:
        opponent_id = 1

    opponent_choices = manager.get_player_choices(game_id, opponent_id)

    # Выбираем шаблон в зависимости от номера игрока
    if player_id == 1:
        return templates.TemplateResponse(
            "player_1.html", 
            {
                "request": request,
                "season": manager.get_season(game_id),
                "product": manager.get_product(),
                "game_id": game_id,
                "player_choices": player_choices,
                "opponent_choices": opponent_choices,
                "cur_round": manager.get_cur_round(game_id)
            }
        )
    else:
        return templates.TemplateResponse(
            "player_2.html", 
            {
                "request": request,
                "season": manager.get_season(game_id),
                "product": manager.get_product(),
                "game_id": game_id,
                "player_choices": player_choices,
                "opponent_choices": opponent_choices,
                "cur_round": manager.get_cur_round(game_id)
            }
        )


@router.post("/submit_price_quality/{game_id}")
async def submit_price_quality(request: Request, game_id: str, player_id: int = Form(...), price: int = Form(...), quality: str = Form(...), advertisement: int = Form(...)):
    """Обработчик POST-запросов, обработка игровых ходов"""
    
    # Логирование полученных данных
    print(f"Данные получены: player_id={player_id}, price={price}, quality={quality}, advertisement={advertisement}")
    manager.player_choices_made[game_id][player_id] = True

    round_num = manager.get_cur_round(game_id)

    # Сохраняем данные игрока
    if 'player_data' not in manager.games[game_id]:
        manager.games[game_id]['player_data'] = {}
    if round_num not in manager.games[game_id]['player_data']:
        manager.games[game_id]['player_data'][round_num] = {}
        
    manager.games[game_id]['player_data'][round_num][player_id] = {
        "price": price,
        "quality": quality,
        "advertisement": advertisement
    }

    response_data = {
        "success": True,
        "choice": {
            "round": round_num,
            "price": price,
            "quality": quality,
            "advertisement": advertisement
        }
    }

    best_player = None

    # Если оба игрока сделали ход
    if len(manager.games[game_id]['player_data'][round_num]) == 2:
        p1 = manager.games[game_id]['player_data'][round_num][1]
        p2 = manager.games[game_id]['player_data'][round_num][2]

        # Расчет результатов раунда
        score_p1 = int(p1["price"]) + int(p1["quality"]) + (int(p1["advertisement"]) / 100)
        score_p2 = int(p2["price"]) + int(p2["quality"]) + (int(p2["advertisement"]) / 100)

        print(f"Результаты раунда {round_num}:")
        print(f"  Игрок 1: {score_p1} (цена={p1['price']}, качество={p1['quality']}, реклама={p1['advertisement']})")
        print(f"  Игрок 2: {score_p2} (цена={p2['price']}, качество={p2['quality']}, реклама={p2['advertisement']})")

        # Определение победителя раунда
        if score_p1 < score_p2:
            best_player = 2
        elif score_p1 > score_p2:
            best_player = 1
        else:
            best_player = random.choice([1, 2])

        # Обновление счетчика побед
        if 'win_counts' not in manager.games[game_id]:
            manager.games[game_id]['win_counts'] = {1: 0, 2: 0}
        manager.games[game_id]['win_counts'][best_player] += 1

        await manager.send_round_result(game_id, best_player)

        if manager.games[game_id]['cur_round'] >= manager.max_rounds:
            win_counts = manager.games[game_id]['win_counts']
            game_winner = None
            
            if win_counts[1] > win_counts[2]:
                game_winner = 1
            elif win_counts[2] > win_counts[1]:
                game_winner = 2
            
            # Отправка результатов игры
            for player_id in manager.games[game_id]['active_connections']:
                if game_winner is None:
                    await manager.send_to_player("draw_page", game_id, player_id)
                elif player_id == game_winner:
                    await manager.send_to_player("win_page", game_id, player_id)
                else:
                    await manager.send_to_player("fail_page", game_id, player_id) 
            
            await manager.end_game(game_id)
        else:
            await manager.end_round(game_id)

    return response_data


@router.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: int):
    """WebSocket-эндпоинт для реального взаимодействия"""
    await manager.connect(game_id, player_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if player_id == 1:
                other_player = 2
            else:
                other_player = 1
            await manager.send_to_player(data, game_id, other_player)
    except WebSocketDisconnect:
        manager.disconnect(game_id, player_id)

