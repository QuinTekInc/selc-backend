
from channels.generic.websocket import WebsocketConsumer
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


        
        self.accept()

    async def disconnect(self, code):
        pass
    
    async def receive(self, text_data = None, bytes_data = None):
        pass

    


