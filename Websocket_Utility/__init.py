from channels.generic.websocket import AsyncJsonWebsocketConsumer 
from asgiref.sync import sync_to_async
import traceback


class LiveConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		try :
			# user_id = self.scope['query_string'].decode('utf-8').split('=')[1]	# Extract ID from query string
			# self.room_group_name = f'wss_group_{user_id}'
			self.room_group_name = 'wss_group'
			self.error_code = 4011
			await self.channel_layer.group_add(self.room_group_name, self.channel_name)
			await self.accept()	  
			await self.send_json({
				"status" : 200,
				'msg' : "connected"
			})
		except :
			pass


	async def disconnect(self, code):
		print("websocket disconnected....",code)
		# await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
		# await self.close(self.error_code)
		# await self.send({
		#	'type' : "websocket.send",
		#	'text' : "Message send to client",
		# }) 


	async def send_live_data(self, event):
		data = event.get('value')
		try:
			await self.send_json(data)
		except Exception as e:
			await self.disconnect({'code': self.error_code})
			await self.close(self.error_code)
	
	async def receive(self, text_data):				  ##### function for get data form websocket
		text_data_json = await self.decode_json(text_data)