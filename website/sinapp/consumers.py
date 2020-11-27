import asyncio
import json
from django.contrib.auth import get_user_model
#from channels.consumer import AsyncConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .InfluxBridge import InfluxBridge

from .models import *

class SINConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		self.groupname='dashboard'
		await self.channel_layer.group_add(
			self.groupname,
			self.channel_name,)
		await self.accept()

		#await self.send({"type":"websocket.accept"})#accept()
		#await asyncio.sleep(3)
		#await self.send({"type":"websocket.send",
		#	"text":"dummy data"})

	async def receive(self, text_data):

		if(text_data == "Initial data needed!"):
			print("LOG: Initial data needed - using InfluxBridge to get them.")
			data = await self.get_initial_data()
			await self.send(text_data=json.dumps(data))
			return

		print("recv", text_data)
		#await self.send(text_data=json.dumps({'value':"Pokus pokusovaty"}))
		datapoint = json.loads(text_data)

		
		await self.channel_layer.group_send(
			self.groupname,
			{
				'type':'deprocessing',
				'value': datapoint
			}
		)


	async def deprocessing(self,event):
		valOther=event['value']
		await self.send(text_data=json.dumps(valOther))
	 
	async def new_message(self, event):
		print("tady nactu hooodne dat")

	async def get_initial_data(self):
		d = InfluxBridge()
		temp = d.get_data(measurement="temperature", fields="value", aggregation="10m")
		temp = d.get_fields(temp, "time", "value")
		hum = d.get_data(measurement="humidity", fields="value", aggregation="10m")
		hum = d.get_fields(hum, "time", "value")
		data = {}
		data["time"] = hum["time"]
		data["temperature"] = temp["value"]
		data["humidity"] = hum["value"]
		return data

