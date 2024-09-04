from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import generics, permissions, status

from .serializers import ChatRoomSerializer, MessageSerializer
from .models import ChatRoom, Message


class CreateChatroomView(generics.CreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListRoomMessages(generics.ListAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        chatroom_id = self.kwargs["chatroom_id"]
        chatroom = ChatRoom.objects.get(id=chatroom_id)
        messages = Message.objects.filter(chatroom=chatroom).all().order_by("-created_at")
        for message in messages:
            if message.sender != user:
                message.is_read = True
                message.save()
        return messages if messages.count() > 0 else []
