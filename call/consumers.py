import json

from channels.generic.websocket import AsyncWebsocketConsumer


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"room_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        payload = json.loads(text_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "room.signal",
                "payload": payload,
                "sender_channel_name": self.channel_name,
            },
        )

    async def room_signal(self, event):
        if event["sender_channel_name"] == self.channel_name:
            return

        await self.send(text_data=json.dumps(event["payload"]))
