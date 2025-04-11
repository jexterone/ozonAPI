import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class TaskStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        logger.info(f"WebSocket connected for task_id: {self.task_id}")

        # Подписываемся на группу для данного task_id
        await self.channel_layer.group_add(
            f'task_{self.task_id}',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected for task_id: {self.task_id} with code: {close_code}")

        # Отписываемся от группы при отключении
        await self.channel_layer.group_discard(
            f'task_{self.task_id}',
            self.channel_name
        )

    async def send_status_update(self, event):
        status = event['status']
        result = event.get('result', '')
        logger.info(f"Sending status update: {status}, result: {result}")
        await self.send(text_data=json.dumps({'status': status, 'result': result}))