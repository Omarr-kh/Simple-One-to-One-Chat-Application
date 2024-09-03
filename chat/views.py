from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import generics, permissions, status

from .serializers import ChatRoomSerializer, MessageSerializer
from .models import ChatRoom, Message


class CreateChatroomView(generics.CreateAPIView):
    serializer_class = ChatRoomSerializer