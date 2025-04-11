from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
from .models import Product, OzonApiKey

BASE_URL = 'https://api-seller.ozon.ru'

@shared_task(bind=True)
def fetch_products_from_ozon(self, client_id, api_key, limit, update=False):
    try:
        headers = {
            'Client-Id': client_id,
            'Api-Key': api_key,
            'Content-Type': 'application/json'
        }

        # Определяем last_page_id для догрузки
        if not update:
            last_product = Product.objects.order_by('-id').first()
            last_page_id = last_product.last_page_id if last_product else None
        else:
            last_page_id = None

        total_products = []
        batch_size = 1000  # Максимум 1000 товаров за раз
        remaining_limit = limit

        while remaining_limit > 0:
            current_limit = min(remaining_limit, batch_size)

            # Запрос к /v3/product/list
            list_url = f'{BASE_URL}/v3/product/list'
            list_payload = {
                "filter": {"visibility": "ALL"},
                "last_id": last_page_id,
                "limit": current_limit
            }
            list_response = requests.post(list_url, headers=headers, json=list_payload)

            if list_response.status_code != 200:
                return {'error': f'Ошибка при запросе к /v3/product/list: {list_response.json()}'}

            list_data = list_response.json().get('result', {})
            items = list_data.get('items', [])

            if not items:
                break

            # Извлекаем product_id
            product_ids = [item['product_id'] for item in items]

            # Запрос к /v3/product/info/list
            info_url = f'{BASE_URL}/v3/product/info/list'
            info_payload = {
                "product_id": product_ids
            }
            info_response = requests.post(info_url, headers=headers, json=info_payload)

            if info_response.status_code != 200:
                return {'error': 'Ошибка при запросе к /v3/product/info/list'}

            detailed_items = info_response.json().get('items', [])
            total_products.extend(detailed_items)

            # Обновляем last_page_id
            last_page_id = list_data.get('last_id')
            if not last_page_id:
                break

            remaining_limit -= current_limit

        # Сохранение данных в базу
        for item in total_products:
            name = item.get('name', '') or 'Без названия'
            price = item.get('price', '0') or '0'

            stocks = item.get('stocks', {}).get('stocks', [])
            quantity = stocks[0].get('present', 0) if stocks else 0

            primary_images = item.get('primary_image', [])
            image_url = primary_images[0] if primary_images else 'https://via.placeholder.com/150'

            Product.objects.update_or_create(
                ozon_id=item['id'],
                defaults={
                    'name': name,
                    'price': float(price),
                    'quantity': quantity,
                    'image_url': image_url,
                    'last_page_id': last_page_id
                }
            )
        task_id = self.request.id
        print(f'task id {task_id}')


        # Отправляем уведомление через WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'task_{task_id}',  # Группа для конкретной задачи
            {
                'type': 'send_status_update',
                'status': 'SUCCESS',
                'result': 'Задача завершена',
            }
        )

        return {'success': True}

    except Exception as e:
        return {'error': str(e)}