from fastapi import WebSocket

class ConnectionManager:

    def __init__(self):
        # user_id to list of connections
        self.active_connections: dict[int, list[dict]] = {}

    async def connect(
        self,
        user_id: int,
        company_id: int,
        websocket: WebSocket,
        is_super_admin: bool = False,
    ):
        await websocket.accept()

        connection = {
            "ws": websocket,
            "company_id": company_id,
            "is_super_admin": is_super_admin,
        }

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(connection)


    def disconnect(self, user_id: int, websocket: WebSocket):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                conn for conn in self.active_connections[user_id]
                if conn["ws"] != websocket
            ]

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]


    async def send_notification(self, user_id: int, message: dict, company_id: int):
        connections = self.active_connections.get(user_id, [])

        for conn in connections:
            # keep tenant isolation, but let verified super admin listen across companies
            if conn.get("is_super_admin") or conn["company_id"] == company_id:
                await conn["ws"].send_json(message)


manager = ConnectionManager()