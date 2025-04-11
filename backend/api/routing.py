from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/task-status/<str:task_id>/', consumers.TaskStatusConsumer.as_asgi()),
]