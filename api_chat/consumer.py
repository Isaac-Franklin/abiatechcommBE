import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from groups.models import Group, GroupChatMessage, GroupMember

User = get_user_model()

class GroupChatConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        print("USER:", self.scope["user"])
        print("AUTH:", self.scope["user"].is_authenticated)
        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]
        self.room_group_name = f"group_chat_{self.group_id}"
        self.user = self.scope["user"]

        print(f"🔌 WebSocket connection attempt")
        print(f"   Group ID: {self.group_id}")
        print(f"   User: {self.user}")
        print(f"   Authenticated: {self.user.is_authenticated if self.user else False}")

        if not self.user.is_authenticated:
            await self.close()
            return

        self.user_id = self.user.id

        # is_member = await self.check_group_membership()
        # if not is_member:
        #     await self.close()
        #     return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"✅ WebSocket ACCEPTED for group {self.group_id}")

        await self.send(text_data=json.dumps({
            "type": "connection",
            "message": "Connected to group chat",
            "group_id": self.group_id
        }))

    async def disconnect(self, close_code):
        print(f"❌ WebSocket disconnected: {close_code}")
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"📨 Received message: {text_data}")
        try:
            data = json.loads(text_data)
            message_text = data.get("message", "").strip()
            message_type = data.get("message_type", "text")

            if not message_text:
                await self.send(json.dumps({
                    "type": "error",
                    "message": "Message cannot be empty"
                }))
                return

            message = await self.save_message(message_text, message_type)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": {
                        "id": message.id,
                        "message": message.message,
                        "message_type": message.message_type,
                        "user": {
                            "id": message.user.id,
                            "username": message.user.username,
                            "email": message.user.email,
                        },
                        "created_at": message.created_at.isoformat(),
                    }
                }
            )

        except Exception as e:
            await self.send(json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "data": event["message"]
        }))

    @database_sync_to_async
    def check_group_membership(self):
        try:
            return GroupMember.objects.filter(
                group_id=self.group_id,
                user_id=self.user_id
            ).exists()
        except Group.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, message_text, message_type):
        group = Group.objects.get(id=self.group_id)
        user = User.objects.get(id=self.user_id)  # ✅ real User

        return GroupChatMessage.objects.create(
            group=group,
            user=user,
            message=message_text,
            message_type=message_type
        )
