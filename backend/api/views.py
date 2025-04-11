from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, OzonApiKey
from .serializers import ProductSerializer
from .tasks import fetch_products_from_ozon

class ProductListView(APIView):
    def get(self, request):
        try:
            # Проверяем, нужно ли загрузить товары из базы данных
            if 'load_products' in request.query_params:
                products = Product.objects.all().order_by('-id')
                serializer = ProductSerializer(products, many=True)
                return Response(serializer.data)

            # Получаем активный ключ API из базы данных
            api_key = OzonApiKey.objects.filter(is_active=True).first()
            if not api_key:
                return Response({'error': 'Активный ключ API не найден'}, status=400)

            # Параметры запроса
            limit = request.query_params.get('limit', 10)
            update = request.query_params.get('update', 'false').lower() == 'true'

            try:
                limit = int(limit)
            except ValueError:
                return Response({'error': 'Неверный формат параметра limit'}, status=400)

            # Запускаем задачу Celery
            task = fetch_products_from_ozon.delay(
                client_id=api_key.client_id,
                api_key=api_key.api_key,
                limit=limit,
                update=update
            )
            return Response({'task_id': task.id}, status=202)

        except Exception as e:
            return Response({'error': str(e)}, status=500)