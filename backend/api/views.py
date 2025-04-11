from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, OzonApiKey
from .serializers import ProductSerializer
from .tasks import fetch_products_from_ozon
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProductListView(APIView):
    @swagger_auto_schema(
        operation_description="Получение списка товаров или запуск задачи для загрузки товаров из API Ozon.",
        manual_parameters=[
            openapi.Parameter(
                'load_products',
                openapi.IN_QUERY,
                description="Загрузить товары из базы данных (true/false)",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
            openapi.Parameter(
                'limit',
                openapi.IN_QUERY,
                description="Количество товаров для загрузки",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'update',
                openapi.IN_QUERY,
                description="Обновить товары (true/false)",
                type=openapi.TYPE_BOOLEAN,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="Список товаров из базы данных",
                schema=ProductSerializer(many=True)
            ),
            202: openapi.Response(
                description="Задача успешно запущена",
                examples={
                    "application/json": {
                        "task_id": "e2dfc53a-51ce-41ab-943f-031460d43726"
                    }
                }
            ),
            400: openapi.Response(
                description="Ошибка в запросе",
                examples={
                    "application/json": {
                        "error": "Активный ключ API не найден"
                    }
                }
            ),
            500: openapi.Response(
                description="Внутренняя ошибка сервера",
                examples={
                    "application/json": {
                        "error": "Internal server error"
                    }
                }
            ),
        }
    )
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
            limit = request.query_params.get('limit', 1)
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