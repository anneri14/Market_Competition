from fastapi import WebSocket
import asyncio
import random
import string
from services.products_generator import product_generator

SEASONS = ["Зима", "Весна", "Лето", "Осень"]

ROUND_TIME = 30
MAX_ROUNDS = 16

class ConnectionManager:
    def __init__(self):
        """Инициализация менеджера"""
        self.active_connections: dict[int, WebSocket] = {}
        self.games = {}
        self.max_rounds = MAX_ROUNDS
        self.player_choices_made = {}

        self.PRICE_INFO = {
            'low': {'coef': 1.3, 'income': 0.7},
            'medium': {'coef': 1, 'income': 1},
            'high': {'coef': 0.7, 'income': 1.3}
        }

        self.QUALITY_INFO = {
            'low': {'coef': 0.7, 'cost': 0},
            'medium': {'coef': 1, 'cost': 50},
            'high': {'coef': 1.3, 'cost': 100}
        }

        self.win_counts = {}

    async def connect(self, game_id: str, player_id: int, websocket: WebSocket) -> None:
        """Создание нового подключения игрока"""
        if not product_generator.products_inited:
            await product_generator.init_products_list()

        if game_id not in self.games:
            self.games[game_id] = {
                'players': {
                    1: {"budget": 1000, "score": 0, "brand": 0},
                    2: {"budget": 1000, "score": 0, "brand": 0}
                }, 
                'active_connections': {},
                'cur_round': 1,
                'is_timer_running': False
            }
            self.win_counts[game_id] = {1: 0, 2: 0}
            
        self.player_choices_made[game_id] = {1: False, 2: False}

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
                print(f"Игра {game_id} завершена и удалена")

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
        round_num = self.games[game_id]['cur_round']

        for player_id in self.games[game_id]['active_connections']:
            await self.send_to_player("Раунд завершён! Ожидайте следующего раунда.", game_id, player_id)
    
            if round_num in self.games[game_id].get('player_data', {}):
                opponent_id = 2 if player_id == 1 else 1
            if round_num in self.games[game_id].get('player_data', {}) and \
            opponent_id in self.games[game_id]['player_data'][round_num]:
                opponent_data = self.games[game_id]['player_data'][round_num][opponent_id]
                await self.send_to_player(
                    f"opponent_actions|{round_num}|"
                    f"{opponent_data['price']}|"
                    f"{opponent_data['quality']}|"
                    f"{opponent_data['advertisement']}",
                    game_id,
                    player_id
                )
        self.games[game_id]['cur_round'] += 1
        self.games[game_id]['timer'] = ROUND_TIME
        self.player_choices_made[game_id] = {1: False, 2: False}

        cur_season = self.get_season(game_id)
        cur_product = self.get_product()
        for player_id in self.games[game_id]['active_connections']:
            await self.send_to_player(f"{ROUND_TIME}|{self.games[game_id]['cur_round']}|{cur_season}|{cur_product}", game_id, player_id)


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

            for player_id in self.games[game_id]['active_connections']:
                await self.send_to_player(f"{self.games[game_id]['timer']}|{self.games[game_id]['cur_round']}|{cur_season}|{cur_product}", game_id, player_id)
    
            while self.games[game_id]['timer'] > 0 and self.games[game_id]['is_timer_running']:
                if len(self.games[game_id].get('player_data', {}).get(self.games[game_id]['cur_round'], {})) == 2:
                    break

                for player_id in self.games[game_id]['active_connections']:
                    await self.send_to_player(f"{self.games[game_id]['timer']}", game_id, player_id)
                await asyncio.sleep(1)
                self.games[game_id]['timer'] -= 1
            
            if game_id not in self.games or not self.games[game_id]['is_timer_running']:
                break

            await self.end_round(game_id)

        if self.games[game_id]['cur_round'] > self.max_rounds:
            await self.end_game(game_id)

    def get_season(self, game_id: str) -> str:
        """Определяем сезон на основе номера раунда"""
        cur_round = self.games[game_id].get('cur_round', 1)

        if 1 <= cur_round <= 4:
            return SEASONS[0]
        elif 5 <= cur_round <= 8:
            return SEASONS[1]
        elif 9 <= cur_round <= 12:
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
                    "quality": players_data[player_id]["quality"],
                    "advertisement": players_data[player_id]["advertisement"]
                })
        return choices
    
    def get_opponent_choice(self, game_id: str, player_id: int, round_num: int):
        """Возвращает выбор противника для конкретного раунда"""
        if game_id not in self.games or 'player_data' not in self.games[game_id]:
            return None
        
        opponent_id = 2 if player_id == 1 else 1
        round_data = self.games[game_id]['player_data'].get(round_num, {})
        
        if opponent_id in round_data:
            return {
                "price": round_data[opponent_id]["price"],
                "quality": round_data[opponent_id]["quality"],
                "advertisement": round_data[opponent_id]["advertisement"]
            }
        return None
    
manager = ConnectionManager()
