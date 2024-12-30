import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from connections.live_data import *
from connections.timeloopController import *

class LiveConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.room_group_name = 'Test_Consumer'
		self.error_code = 4011
		await self.channel_layer.group_add(self.room_group_name, self.channel_name)
		await self.accept()

		await self.send_json({'connection' : json.dumps({"msg" : "...CONNECTED..."})})

		# self.exp_date = self.scope['url_route']['kwargs']['exp_date']
	async def disconnect(self, code):
		await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
		await self.close(self.error_code)
		

	async def send_live_data(self, event):
		data = event.get('value')
		try:
			await self.send_json(data)
		except Exception as e:
			await self.disconnect({'code': self.error_code})
			await self.close(self.error_code)