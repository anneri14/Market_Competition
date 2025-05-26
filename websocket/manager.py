from fastapi import WebSocket
import asyncio
import random

SEASONS = ["Зима", "Весна", "Лето", "Осень"]
PRODUCTS = ["Сноуборд", "Велосипед", "Солнечные очки", "Зонт и дождевик", "Новогодние украшения", "Школьные принадлежности", "Пуховик", "Гамаки и шезлонги", "Термос", "Семена и рассада"]

ROUND_TIME = 20
MAX_ROUNDS = 24


class ConnectionManager:
    def __init__(self):
        """Инициализация менеджера"""
        self.active_connections: dict[int, WebSocket] = {}
        self.timer = ROUND_TIME
        self.is_timer_running = False
        self.cur_round = 1
        self.max_rounds = MAX_ROUNDS
        self.player_data = {}
        self.games = {}

    async def connect(self, player_id: int, websocket: WebSocket) -> None:
        """Создание нового подключения игрока"""
        if player_id in self.active_connections:
            return

        await websocket.accept()
        self.active_connections[player_id] = websocket

        print(f"Игрок {player_id} подключен")

        if not self.is_timer_running and len(self.active_connections) == 2:
            self.is_timer_running = True
            self.timer = 20
            asyncio.create_task(self.start_timer())

    def disconnect(self, player_id: int) -> None:
        """Удаление подключения игрока"""
        if player_id in self.active_connections:
            del self.active_connections[player_id]

            print(f"Игрок {player_id} отключен")

            if not self.active_connections:
                self.is_timer_running = False
                self.timer = 20

    async def send_to_player(self, message: str, player_id: int) -> None:
        """Отправка сообщения игроку"""
        if player_id in self.active_connections:
            await self.active_connections[player_id].send_text(message)

    async def send_round_result(self, best_player: int) -> None:
        """Отправка результата раунда обоим игрокам"""
        message = f"Лучший игрок: Игрок {best_player}"
        for player_id in [1, 2]:
            await self.send_to_player(message, player_id)

    async def end_game(self) -> None:
        """Завершение игры и отключение всех игроков"""
        for player_id in self.active_connections:
            await self.send_to_player("Игра окончена!", player_id)
            self.disconnect(player_id)


    async def start_timer(self) -> None:
        """Запуск таймера"""
        while self.is_timer_running and self.cur_round <= self.max_rounds:
            self.timer = 20

            cur_season = self.get_season()
            cur_product = self.get_product()

            while self.timer > 0 and self.is_timer_running:
                for player_id in self.active_connections:
                    await self.send_to_player(f"{self.timer}|{self.cur_round}|{cur_season}|{cur_product}", player_id)
                await asyncio.sleep(1)
                self.timer -= 1
            
            if not self.is_timer_running:
                break

            self.cur_round += 1

        if self.cur_round > self.max_rounds:
            await self.end_game()

    def get_season(self) -> str:
        """Определяем сезон на основе номера раунда"""
        if 1 <= self.cur_round <= 6:
            return SEASONS[0]
        elif 7 <= self.cur_round <= 12:
            return SEASONS[1]
        elif 13 <= self.cur_round <= 18:
            return SEASONS[2]
        else:
            return SEASONS[3]
        
    def get_product(self) -> str:
        """Рандомным образом определяем товар"""
        return random.choice(PRODUCTS)
    
    def create_game_id(self) -> str:
        """Создаем уникальный ID игры"""
        while True:
            game_id = str(random.randint(100000, 999999))
            if game_id not in self.games:
                self.games[game_id] = []
                return game_id
    
    def join_game(self, game_id: str) -> int:
        """Возвращает номер игрока (1 или 2) или 0 если нельзя присоединиться"""
        if game_id not in self.games:
            return 0
        
        return 1
    
manager = ConnectionManager()