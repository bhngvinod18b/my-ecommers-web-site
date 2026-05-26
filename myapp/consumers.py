import json
from channels.generic.websocket import AsyncWebsocketConsumer


class OrderConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.group_name = "manager_notifications"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        print("🔥 Manager connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_order_notification(self, event):
        print("📩 Event received:", event)

        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))