from fastapi import WebSocket
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}
        self.timer = 20 
        self.is_timer_running = False

        self.cur_round = 1

    async def connect(self, player_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[player_id] = websocket
        print(f"Игрок {player_id} подключен")
        if not self.is_timer_running:
            self.is_timer_running = True
            self.timer = 20
            asyncio.create_task(self.start_timer())

    def disconnect(self, player_id: int):
        if player_id in self.active_connections:
            del self.active_connections[player_id]
            print(f"Игрок {player_id} отключен")
            if not self.active_connections:
                self.is_timer_running = False
                self.timer = 20

    async def send_to_player(self, message: str, player_id: int):
        if player_id in self.active_connections:
            await self.active_connections[player_id].send_text(message)

    async def start_timer(self):
        while self.is_timer_running:
            while self.timer > 0:
                for player_id in self.active_connections:
                    await self.send_to_player(f"{self.timer}|{self.cur_round}", player_id)
                await asyncio.sleep(1)
                self.timer -= 1
            
            self.cur_round += 1
            self.timer = 20

            for player_id in self.active_connections:
                await self.send_to_player(f"{self.timer}|{self.cur_round}", player_id)

        

manager = ConnectionManager()