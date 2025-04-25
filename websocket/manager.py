from fastapi import WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.timer = 20 
        self.is_timer_running = False

    async def connect(self, player_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[player_id] = websocket
        print(f"Игрок {player_id} подключен")
        if not self.is_timer_running:  # Запускаем таймер только если он не запущен
            self.is_timer_running = True
            asyncio.create_task(self.start_timer())

    def disconnect(self, player_id: int):
        if player_id in self.active_connections:
            del self.active_connections[player_id]
            print(f"Игрок {player_id} отключен")
            if not self.active_connections:  # Если нет активных подключений, останавливаем таймер
                self.is_timer_running = False
                self.timer = 20 # Сброс таймера

    async def send_to_player(self, message: str, player_id: int):
        if player_id in self.active_connections:
            await self.active_connections[player_id].send_text(message)

    async def start_timer(self):
        while self.is_timer_running and self.timer > 0:  # Проверяем флаг перед каждым шагом
            if not self.active_connections:  
                self.timer = 20
                break
            if self.timer <= 0:
                self.timer = 20
                
            await asyncio.sleep(1)
            self.timer -= 1
            for player_id in self.active_connections:
                await self.send_to_player(str(self.timer), player_id)
        

manager = ConnectionManager()