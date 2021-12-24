import json
from channels.consumer import SyncConsumer, AsyncConsumer
from channels.exceptions import StopConsumer
from asgiref.sync import async_to_sync

class ChatConsumer(AsyncConsumer):
	async def websocket_connect(self, event):
		self.user = self.scope['user']
		self.chat_id = self.scope['url_route']['kwargs']['chat_id']
		self.chat_room_id = f"chat_{self.chat_id}"


		await self.channel_layer.group_add(
				self.chat_room_id,
				self.channel_name
		)


		await self.send({
				'type': 'websocket.accept'
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
