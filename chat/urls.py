from django.urls import path
from .views import index, create_chat, chat, leave_chat

app_name = 'chat'

urlpatterns = [
	path('', index, name='index'),
	path('create/', create_chat, name='create_chat'),
	path('<str:chat_id>/', chat, name='chat'),
	path('<str:chat_id>/leave/', leave_chat, name='leave_chat'),
]