import datetime
import json
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from .models import GroupCaht, Message


class ChatConsumer(AsyncConsumer):
	async def websocket_connect(self, event):
		self.user = self.scope['user']
		self.chat_id = self.scope['url_route']['kwargs']['chat_id']
		self.chat = await self.get_chat()
		self.chat_room_id = f"chat_{self.chat_id}"



		if self.chat:
			await self.channel_layer.group_add(
					self.chat_room_id,
					self.channel_name
			)


			await self.send({
					'type': 'websocket.accept'
			})
		else:
			await self.send({
				'type': 'websocket.close'
			})


	async def websocket_disconnect(self, event):
		await self.channel_layer.group_discard(
			self.chat_room_id,
			self.channel_name
		)
		raise StopConsumer()

	async def websocket_receive(self, event):
		text_data = event.get('text', None)
		bytes_data = event.get('bytes', None)

		if text_data:
			text_data_json = json.loads(text_data)
			text = text_data_json['text']

			await self.create_message(text)

			await self.channel_layer.group_send(
				self.chat_room_id,
				{
					'type': 'chat_message',
					'message': json.dumps({'type': "msg", 'sender': self.user.username, 'text': text}),
					'sender_channel_name': self.channel_name
				}
			)

			
	
	async def chat_message(self, event):
		message = event['message']

		if self.channel_name != event['sender_channel_name']:
			await self.send({
					'type': 'websocket.send',
					'text': message
			})

	async def chat_activity(self, event):
		message = event['message']

		await self.send({
			'type': 'websocket.send',
			'text': message
		})


	@database_sync_to_async
	def get_chat(self):
		try:
			chat = GroupCaht.objects.get(unique_code=self.chat_id)
			return chat
		except GroupCaht.DoesNotExist:
			return None

	@database_sync_to_async	
	def create_message(self, text):
		Message.objects.create(chat_id=self.chat.id, author_id=self.user.id, text=text)

# Video Call Status
VC_CONTACTING, VC_NOT_AVAILABLE, VC_ACCEPTED, VC_REJECTED, VC_BUSY, VC_PROCESSING, VC_ENDED = \
	0, 1, 2, 3, 4, 5, 6

class VideoChatConsumer(AsyncConsumer):
	"""docstring for VideoChatConsumer"""
	async def websocket_connect(self, event):
		self.user = self.scope['user']
		self.user_room_id = f"videochat_{self.user.id}"


		await self.channel_layer.group_add(
			self.user_room_id,
			self.channel_name
		)


		await self.send({
			'type': 'websocket.accept'
		})


	async def chat_message(self, event):
		message = event['message']

		await self.send({
				'type': 'websocket.send',
				'text': message
		})		

	@database_sync_to_async
	def get_videothread(self, id):
		try:
			videothread = VideoThread.objects.get(id=id)
			return videothread
		except VideoThread.DoesNotExist:
			return None
		
	@database_sync_to_async
	def create_videothread(self, callee_username):
		try:
			callee = User.objects.get(username=callee_username)
		except User.DoesNotExist:
			return 404, None

		if VideoThread.objects.filter(Q(caller_id=callee.id) | Q(callee_id=callee.id), status=VC_PROCESSING).count() > 0:
			return VC_BUSY, None

		videothread = VideoThread.objects.create(caller_id=self.user.id, callee_id=callee.id)
		self.scope['session']['video_thread_id'] = videothread.id
		self.scope['session'].save()

		return VC_CONTACTING, videothread.id

	@database_sync_to_async
	def change_videothread_status(self, id, status):
		try:
			videothread = VideoThread.objects.get(id=id)
			videothread.status = status
			videothread.save()
			return videothread
		except VideoThread.DoesNotExist:
			return None

	@database_sync_to_async
	def change_videothread_datetime(self, id, is_start):
		try:
			videothread = VideoThread.objects.get(id=id)
			if is_start:
				videothread.date_start = datetime.now()
			else:
				videothread.date_end = datetime.now()

			videothread.save()
			return videothread
		except VideoThread.DoesNotExist:
			return None
