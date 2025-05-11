from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import DenyConnection
from channels.db import database_sync_to_async
import json
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from asgiref.sync import sync_to_async
from project.documents.models import ChatMessage
from project.documents.tasks import save_message_task


class DocumentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            raise DenyConnection('Неавторизованный пользователь')

        self.user_group_name = f'user_{user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def document_created(self, event):
        await self.send(text_data=json.dumps({
            'type': 'document_created',
            'document_id': event['document_id'],
            'title': event['title'],
        }))


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            raise DenyConnection('Неавторизованный пользователь')
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        user = self.scope['user']
        if isinstance(user, AnonymousUser):
            raise DenyConnection('Неавторизованный пользователь')

        # await self.save_message(user, self.room_name, message)
        message_created_at = timezone.now()
        await database_sync_to_async(save_message_task.delay)(user.id, message, self.room_name,
                                                               message_created_at )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username
            }
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    'message': event['message'],
                    'username': event['username']
                }
            )
        )
