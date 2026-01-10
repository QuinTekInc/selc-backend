
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json 

from django.contrib.auth.models import User


#consumer for the dashboard for the lecturer dashboard.
class LDashboardGraphDataConsumer(WebsocketConsumer):
    def connect(self):

        user: User = self.scope['user']

        if user is None:
            self.close()

        if user.is_anonymous or not user.is_authenticated or not user.groups.filter(name='lecturer').exists():
            # Reject the connection 
            self.close()
            pass

        self.group_name = f'lecturer_dashboard_{user.username}' #each lecturer has their own group.
        
        self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        self.accept()


    async def disconnect(self, code):
        self.channel_layer.group_discard( 
            self.group_name, 
            self.channel_name
        )
        pass
    
    async def receive(self, text_data = None, bytes_data = None):
        #nothing to receive here.
        pass

    
    def lecturer_dashboard_event(self, event):
        self.send(text_data=json.dumps(event['data']))
        pass

    


