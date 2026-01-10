
#consumer's for administrators

from channels.generic.websocket import WebsocketConsumer
import json 

from django.contrib.auth.models import User


#this consumer show the graph data for the dashboard for the admin dashboard.
class DashboardGraphConsumer(WebsocketConsumer):

    async def connect(self):

        user: User = self.scope['user']

        if user is None: 
            self.close()


        if user.is_anonymous or not (user.is_authenticated and user.groups.filter(name__in=['superuser', 'admin']).exists()):
            self.close() 
            pass 

        
        self.group_name = 'admin_dashboard'

        self.channel_layer.group_add(self.group_name, self.channel_name)
        
        await self.accept()


    async def disconnect(self, code):
        self.channel_layer.group_discard( 
            self.group_name, 
            self.channel_name
        )
        pass



    async def receive(self, text_data=None, byte_data=None):
        #nothing to receive here.
        pass
    
    def admin_dashoard_event(self, event):
        self.send(text_data=json.dumps(
            event['data']
        ))
        pass
