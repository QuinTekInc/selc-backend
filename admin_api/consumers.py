
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

        await self.accept()

        self.send(
            text_data=json.dumps({
                'type': 'connection_status',
                'mesage': 'Connection established with dasboard consumer'
            })
        )


    async def disconnect(self, code):
        pass



    async def receive(self, text_data=None, byte_data=None):

        data = json.loads(text_data)

        # Process the received data and send a response if needed

        await self.send(text_data=json.dumps({
            'message': 'Data received',
            'data': data
        }))
