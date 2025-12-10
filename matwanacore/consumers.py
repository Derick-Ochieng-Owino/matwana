import json
from channels.generic.websocket import AsyncWebsocketConsumer

class RouteVehiclesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # expected path /ws/route/<route_id>/
        self.route_id = self.scope['url_route']['kwargs']['route_id']
        self.group_name = f'route_{self.route_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def vehicle_update(self, event):
        # event['data'] is JSON serializable data about vehicle
        await self.send(text_data=json.dumps(event['data']))
