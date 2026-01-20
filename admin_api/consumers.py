
#consumer's for administrators

from channels.generic.websocket import WebsocketConsumer
from channels.db import database_sync_to_async
import json 
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


#this consumer show the graph data for the dashboard for the admin dashboard.
class DashboardGraphConsumer(WebsocketConsumer):

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        try:
            return Token.objects.get(key=token_key).user
        except Token.DoesNotExist:
            return None
        pass 

    @database_sync_to_async 
    def perform_db_operation(opr_func):
        return (lambda : opr_func)()


    async def connect(self):

        token_key = self.scope['url_route']['kwargs']['token']

        print('User Token: ', token_key)

        user: User = await self.get_user_from_token(user_token)

        if user is None: 
            print('Closing the request because the user information is none')
            #await self.close()
            return

        is_eligible: bool = await database_sync_to_async(lambda : user.groups.filter(name__in=['superuser', 'admin']).exists())()


        if not is_eligible:
            print('User is not eligible to connect to this consumer')
            #await self.close() 
            return

        
        self.group_name = 'admin_dashboard' #basically superuser or admin is added to the group.
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        await self.accept()
        
        pass


    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard( 
                self.group_name, 
                self.channel_name
            )
        except: 
            await self.close()
        
        pass



    def receive(self, text_data=None, byte_data=None):
        #nothing to receive here.
        pass
    
    def admin_dashoard_event(self, event):
        self.send(text_data=json.dumps(
            event['data']
        ))
        pass



class TestConsumer(WebsocketConsumer):

    async def connect(self):
        
        print('Before acceptance')

        await self.accept()

        print('After acceptance')

        for i in range(0, 10):
            await self.send(text_data=json.dumps({
                'motherfucker'
                }))
            pass 

        pass

    async def disconnect(self, close_code):
        await self.close()

    async def receive(self, text_data=None, byte_data=None):
        pass 
