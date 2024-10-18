import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user_group_name = f'user_{self.scope["user"].id}'
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"WebSocket connected for user {self.scope['user'].id}")
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        print(f"WebSocket disconnected for user {self.scope['user'].id}")

    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
        print(f"Notification sent to user {self.scope['user'].id}: {message}")


#Tolerante a fallos
class HeartbeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
            self.heartbeat_task = asyncio.create_task(self.heartbeat())
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'heartbeat_task'):
            self.heartbeat_task.cancel()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'pong':
            self.last_pong = asyncio.get_event_loop().time()

    async def heartbeat(self):
        while True:
            await self.send(json.dumps({'type': 'ping'}))
            await asyncio.sleep(5)  # Envía un ping cada 5 segundos