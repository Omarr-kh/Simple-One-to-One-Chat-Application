import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import ChatRoom, Message
from .serializers import MessageSerializer


@sync_to_async
def get_user(token):
    return Token.objects.get(key=token).user


@sync_to_async
def last_10_message(chatroom):
    try:
        chatroom = ChatRoom.objects.get(id=chatroom)
        messages = chatroom.messages.all().order_by("-created_at")[:10]
        if messages.count() > 0:
            messages_data = MessageSerializer(messages, many=True).data
            return messages_data
        else:
            return {}
    except ChatRoom.DoesNotExist:
        return None


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope["url_route"]["kwargs"]["chat_room_id"]
        self.room_group_name = f"chatroom_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        messages = await last_10_message(self.room_id)
        await self.send(
            text_data=json.dumps(
                {
                    "type": "last_50_messages",
                    "messages": messages,
                }
            )
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json["message"]

        message = await self.save_message(message_content)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message_content,
                "user": self.user.username,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        user = event["user"]

        await self.send(
            text_data=json.dumps(
                {
                    "user": user,
                    "message": message,
                }
            )
        )

    @database_sync_to_async
    def save_message(self, message_content):
        # Get the chatroom instance
        chatroom = ChatRoom.objects.get(id=self.room_id)

        # user = self.user
        # user2 = User.objects.create_user(username="test9", password="test12345")

        message = Message.objects.create(
            chatroom=chatroom,
            content=message_content,
            sender=self.user,
            # receiver=user2,
            receiver=(
                chatroom.receiver if chatroom.sender == self.user else chatroom.sender
            ),
        )

        chatroom.last_message = message_content
        chatroom.last_message_date = message.created_at
        chatroom.save()

        return message
