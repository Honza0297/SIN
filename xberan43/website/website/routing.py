from django.conf.urls import url
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from sinapp.consumers import SINConsumer

application = ProtocolTypeRouter({
	'websocket':AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter(
				[
				url("SIN", SINConsumer.as_asgi()),
				])
			)
		)
	}) 