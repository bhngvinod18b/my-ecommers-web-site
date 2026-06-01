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
    async def send_delete_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))
        
class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.group_name = "manager_notifications"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def send_order_notification(self, event):

        await self.send(text_data=json.dumps({
            'message': event['message']
        }))
        

class UpdateConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.group_name = f"user_{self.scope['user'].id}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()


    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )


    async def send_status_update(self, event):

        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))