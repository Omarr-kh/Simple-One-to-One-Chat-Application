from django.urls import path
from . import views

urlpatterns = [
    path(
        "chatrooms/create", views.CreateChatroomView.as_view(), name="create-chatroom"
    ),
    path(
        "chatroom/<int:chatroom_id>/messages",
        views.ListRoomMessages.as_view(),
        name="list-messages",
    ),
]
