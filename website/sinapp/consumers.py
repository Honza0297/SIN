import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer

from channels.db import database_sync_to_async

from .models import *

class SINConsumer(AsyncConsumer):
	async def websocket_connect(self, event):
		print("connection", event)
		print(self.scope)
		await self.send({"type":"websocket.accept"})#accept()
		await asyncio.sleep(3)
		await self.send({"type":"websocket.send",
			"text":"dummy data"})

	async def websocket_receive(self, event):
		print("receive in backend: ", event)
		print(self.scope)
		await self.send({"type":"websocket.send",
			"text":"dummy data from another string?"})

	 
	async def websocket_disconnect(self, event):
		print("disconnect",event)
		print(self.scope)
		await self.send({"type":"websocket.disconnect"})