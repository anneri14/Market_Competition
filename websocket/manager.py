from fastapi import WebSocket
import asyncio
import random
import string
from services.products_generator import product_generator

SEASONS = ["Зима", "Весна", "Лето", "Осень"]

ROUND_TIME = 20
MAX_ROUNDS = 24

class ConnectionManager:
    def __init__(self):
        """Инициализация менеджера"""
        self.active_connections: dict[int, WebSocket] = {}
        self.games = {}
        self.max_rounds = MAX_ROUNDS
        self.player_choices_made = {}

    async def connect(self, game_id: str, player_id: int, websocket: WebSocket) -> None:
        """Создание нового подключения игрока"""
        if not product_generator.products_inited:
            await product_generator.init_products_list()

        if game_id not in self.games:
            self.games[game_id] = {
                'players': {}, 
                'active_connections': {},
                'cur_round': 1,
                'is_timer_running': False
            }

        if player_id in self.games[game_id]['active_connections']:
            return

        await websocket.accept()
        self.games[game_id]['active_connections'][player_id] = websocket


        print(f"Игрок {player_id} подключен к игре {game_id}")

        if len(self.games[game_id]['active_connections']) == 2:
            self.games[game_id]['is_timer_running'] = True
            asyncio.create_task(self.start_game_timer(game_id))

    def disconnect(self, game_id: str, player_id: int) -> None:
        """Удаление подключения игрока"""
        if game_id in self.games and player_id in self.games[game_id]['active_connections']:
            del self.games[game_id]['active_connections'][player_id]
            print(f"Игрок {player_id} отключен от игры {game_id}")

            if not self.games[game_id]['active_connections']:
                self.games[game_id]['is_timer_running'] = False
                del self.games[game_id]
                print(f"Игры {game_id} завершена и удалена")

    async def send_to_player(self, message: str, game_id: str, player_id: int) -> None:
        """Отправка сообщения игроку"""
        if game_id in self.games and player_id in self.games[game_id]['active_connections']:
            await self.games[game_id]['active_connections'][player_id].send_text(message)

    async def send_round_result(self, game_id: str, best_player: int) -> None:
        """Отправка результата раунда обоим игрокам"""
        message = f"Лучший игрок: Игрок {best_player}"
        for player_id in self.games[game_id]['active_connections']:
            await self.send_to_player(message, game_id, player_id)

    async def end_game(self, game_id: str) -> None:
        """Завершение игры и отключение всех игроков"""
        for player_id in self.games[game_id]['active_connections']:
            await self.send_to_player("Игра окончена!", game_id, player_id)
            self.disconnect(game_id, player_id)

    async def end_round(self, game_id: str) -> None:
        """Завершение раунда и сброс состояния выбора игроков"""
        for player_id in self.games[game_id]['active_connections']:
            await self.send_to_player("Раунд завершён! Ожидайте следующего раунда.", game_id, player_id)
    
        self.player_choices_made[game_id] = {1: False, 2: False}


    async def start_game_timer(self, game_id: str) -> None:
        """Запуск таймера для игры"""
        
        self.games[game_id]['cur_round'] = 1
        self.games[game_id]['timer'] = ROUND_TIME
        self.player_choices_made[game_id] = {1: False, 2: False}


        while self.games[game_id]['is_timer_running'] and self.games[game_id]['cur_round'] <= self.max_rounds:
            if game_id not in self.games:
                break
        
            cur_season = self.get_season(game_id)
            cur_product = self.get_product()

            while self.games[game_id]['timer'] > 0 and self.games[game_id]['is_timer_running']:
                for player_id in self.games[game_id]['active_connections']:
                    await self.send_to_player(f"{self.games[game_id]['timer']}|{self.games[game_id]['cur_round']}|{cur_season}|{cur_product}", game_id, player_id)
                await asyncio.sleep(1)
                self.games[game_id]['timer'] -= 1
            
            if game_id not in self.games or not self.games[game_id]['is_timer_running']:
                break

            self.games[game_id]['cur_round'] += 1
            self.games[game_id]['timer'] = ROUND_TIME
            self.player_choices_made[game_id] = {1: False, 2: False}

        await self.end_round(game_id)

        if self.games[game_id]['cur_round'] > self.max_rounds:
            await self.end_game(game_id)

    def get_season(self, game_id: str) -> str:
        """Определяем сезон на основе номера раунда"""
        cur_round = self.games[game_id].get('cur_round', 1)

        if 1 <= cur_round <= 6:
            return SEASONS[0]
        elif 7 <= cur_round <= 12:
            return SEASONS[1]
        elif 13 <= cur_round <= 18:
            return SEASONS[2]
        else:
            return SEASONS[3]
        
    def get_product(self) -> str:
        """Рандомным образом определяем товар"""
        return product_generator.get_random_product()
    
    def create_game_id(self) -> str:
        """Создаем уникальный ID игры"""
        symb = string.digits + string.ascii_letters
        while True:
            game_id = ''.join(random.choice(symb) for _ in range(10))
            if game_id not in self.games:
                self.games[game_id] = {
                    'active_connections': {},
                    'cur_round': 1,
                    'is_timer_running': False,
                    'player_data': {},
                    'timer': ROUND_TIME
                }
                return game_id
    
    def join_game(self, game_id: str) -> int:
        """Возвращает номер игрока или 0 если нельзя присоединиться"""
        if game_id not in self.games:
            return 0
        
        if len(self.games[game_id]['active_connections']) < 2:
            player_id = len(self.games[game_id]['active_connections']) + 1
            return player_id
        return 0
    
    def get_cur_round(self, game_id: str):
        if game_id in self.games:
            return self.games[game_id]['cur_round']
        else:
            return 0
        
    def get_player_choices(self, game_id: str, player_id: int):
        """Возвращает список выборов игрока"""
        if game_id not in self.games or 'player_data' not in self.games[game_id]:
            return []
        
        choices = []
        for round_num, players_data in self.games[game_id]['player_data'].items():
            if player_id in players_data:
                choices.append({
                    "round": round_num,
                    "price": players_data[player_id]["price"],
                    "quality": players_data[player_id]["quality"]
                })
        return choices
    
manager = ConnectionManager()