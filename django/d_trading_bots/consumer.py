import os, sys
import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync

class BaseConsumer(WebsocketConsumer):
    def connect(self):
        self.channel_uuid = self.scope['url_route']['kwargs']['channel_uuid']
        self.channel_mux = self.scope['url_route']['kwargs']['channel_mux']

        # Join group
        async_to_sync(self.channel_layer.group_add)(
            self.channel_uuid,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_uuid,
            self.channel_name
        )

    def receive(self, text_data):
        pass

    # 'type' function
    def forward_msg(self, event):
        try:
            message = event['message']
            channel_mux = event['channel_mux']
            if channel_mux == self.channel_mux:
                # Forward message to WebSocket FE
                self.send(text_data=json.dumps({
                    'message': message
                }))
        except:
            pass
