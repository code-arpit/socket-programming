from fastapi import WebSocket
from typing import Dict, Any
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[Any, Any] = {}
        self.root_connection: WebSocket = None

    async def update_connection(
        self, client_id: str, conversation_id: str, client_port: int
    ):
        connection = self.active_connections.get((client_id, ""), None)
        if connection:
            self.active_connections[
                (client_id, conversation_id, client_port)
            ] = connection

    async def connect(
        self,
        websocket: WebSocket,
        type: str | None = None,
        client_id: str | None = None,
        conversation_id: str | None = "",
        client_port: int | None = None,
    ) -> None:
        await websocket.accept()
        if type == "root":
            self.root_connection = websocket
        else:
            self.active_connections[
                (str(client_id), conversation_id, client_port)
            ] = websocket

    async def disconnect(
        self,
        websocket: WebSocket,
        type: str | None = None,
    ) -> None:
        if type == "root":
            self.root_connection = None
        else:
            connection_key = None
            for key, value in self.active_connections.items():
                if value == websocket:
                    connection_key = key

            if connection_key:
                self.active_connections.pop(connection_key)

    async def receive(self, websocket: WebSocket):
        received_data = await websocket.receive_text()
        return received_data

    async def receive_root(self):
        received_data = await self.root_connection.receive_text()
        return received_data

    async def send_personal_json(
        self,
        data: Dict[str, Any],
        websocket: WebSocket,
        client_id: str | None = None,
        conversation_id: str | None = None,
        client_port: int | None = None,
        status: str | None = None,
    ):
        if client_id:
            websocket = self.active_connections.get(
                (client_id, conversation_id, client_port), None
            )
            if not websocket:
                websocket = self.active_connections.get(
                    (client_id, "", client_port), None
                )
            if websocket:
                await websocket.send_json(data)
        else:
            await websocket.send_json(data)

        # Importing necessary files here to avoid circular imports
        import models
        import services
        from database import SessionLocal

        db = SessionLocal()
        # Updating the client message received from the root user to be stored into database
        if data.get("sender", None) == "AI":
            if data.get('message_id', None):
                message_db_obj = await services.get(
                    db=db,
                    id=data.get('message_id'),
                    model=models.Message,
                )
                if message_db_obj:
                    await services.update(
                        db=db,
                        db_obj=message_db_obj,
                        obj_in={
                            "answer": data.get('message', None),
                            "answer_time": datetime.now(),
                            "status": status,
                        },
                    )
        
        return data

    async def send_root(self, data: Dict[str, Any]):
        try:
            data = await self.root_connection.send_json(data)
            return data
        except Exception as e:
            raise e


connection_manager = ConnectionManager()
