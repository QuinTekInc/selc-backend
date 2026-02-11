# consumer's for administrators

from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync, sync_to_async
import json

from asgiref.sync import async_to_sync


# this consumer show the graph data for the dashboard for the admin dashboard.
class AdminDashboardGraphConsumer(AsyncWebsocketConsumer):
    group_name = None

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        from rest_framework.authtoken.models import Token
        try:
            return Token.objects.get(key=token_key).user
        except Token.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_eligible(self, user):
        user_role = user.groups.filter(name__in=['superuser', 'admin'])
        return user_role.exists()

    async def connect(self):

        # token_key = self.scope["url_route"]["kwargs"]["token"]

        token_key = None

        # retrieving the token for the headers of websocket scope
        headers = dict((k.decode(), v.decode()) for k, v in self.scope['headers'])

        try:
            token_key = headers['authorization'].split(' ')[1]
        except KeyError:
            await self.close(reason='Could not retrieve token from headers.')
            pass

        user = await self.get_user_from_token(token_key)

        if not user:
            await self.close(reason='Could not verify user')
            return

        if not await self.is_user_eligible(user):
            await self.close(reason='You do not qualify to connect to this consumer')
            return

        self.group_name = "admin_dashboard"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        initial_data = await self.get_initial_dashboard_data()

        # send the initial data
        await self.send(text_data=json.dumps(initial_data))

        pass

    async def disconnect(self, close_code):
        if self.group_name is not None:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            pass
        pass


    async def admin_dashboard_event(self, event):
        await self.send(text_data=json.dumps(event["data"]))
        pass

    async def department_dashboard_event(self, event):

        event_data = event['data']
        
        #add the type to the event_data
        event_data['type'] = 'department_dashboard'

        await self.send(text_data=json.dumps(event_data))


    def receive(self, text_data=None, byte_data=None):
        # nothing to receive here.
        pass


    @database_sync_to_async
    def get_initial_dashboard_data(self):
        from selc_core.models import ClassCourse  # import inside method
        from .core_utils import create_classes_chart_info

        # Fetch current class courses
        class_courses = ClassCourse.getCurrentClassCourses()

        # Create the dashboard chart info
        return create_classes_chart_info(class_courses)

    pass







class LecturerDashboardGraphDataConsumer(AsyncWebsocketConsumer):

    group_name = None

    @database_sync_to_async
    def get_user_from_token(self, key: str):
        from rest_framework.authtoken.models import Token
        try:
            return Token.objects.get(key=key).user
        except Token.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_eligible(self, user):
        return user.groups.filter(name='lecturer').exists()

    async def connect(self):

        headers = dict((k.decode(), v.decode()) for k, v in self.scope['headers'])

        token_key = None

        try:
            token_key = headers['authorization'].split(' ')[1]
        except KeyError:
            await self.close(reason='Could not retrieve token from headers.')
            pass


        self.user = await self.get_user_from_token(token_key)

        if self.user is None:
            await self.close()

        if not (await self.is_user_eligible(self.user)):
            # Reject the connection
            await self.close()
            pass

        self.group_name = f'lecturer_dashboard_{self.user.username}'  # each lecturer has their own group.

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        initial_data = await self.get_initial_dashboard_data()

        # send the initial data
        await self.send(text_data=json.dumps(initial_data))

        pass




    async def disconnect(self, code):
        if self.group_name:
            self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        pass

    async def receive(self, text_data=None, bytes_data=None):
        # nothing to receive here.
        pass


    async def lecturer_dashboard_event(self, event):
        await self.send(text_data=json.dumps(event['data']))
        pass


    @database_sync_to_async
    def get_initial_dashboard_data(self):
        from .models import Lecturer, ClassCourse
        from .core_utils import create_classes_chart_info

        lecturer = Lecturer.objects.get(user=self.user)

        class_courses = ClassCourse.getCurrentClassCourses().filter(lecturer=lecturer)

        return create_classes_chart_info(class_courses)

    pass





class TestConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

        for i in range(10):
            await self.send(text_data=json.dumps({
                "count": i
            }))

    async def disconnect(self, close_code):
        pass
