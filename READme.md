# 📌 Ozon API Integration Project

Проект представляет собой интеграцию с API Ozon для автоматической загрузки товаров, их сохранения в базе данных и отображения на фронтенде.

## 🔹 Основная логика

Проект реализует следующие ключевые функции:

Загрузка товаров из API Ozon :
Используется внешний API Ozon для получения данных о товарах.
Данные сохраняются в базу данных PostgreSQL через Django ORM.
Для оптимизации используются асинхронные задачи Celery.
Кэширование и оптимизация :
Redis используется как брокер сообщений для Celery и для кэширования повторных запросов.
WebSocket уведомления позволяют пользователю получать уведомления о завершении задач.
Удобный интерфейс :
Swagger-документация предоставляет детальное описание API.
Фронтенд на React.js позволяет просматривать товары и управлять задачами.
Обработка ошибок :
Валидация входных данных (например, limit, update).
Проверка активного ключа API перед выполнением задач.
Возврат соответствующих HTTP-статусов (400, 404, 500).

## ✅ Основные функции

GET /api/products/ :
Получение списка товаров или запуск задачи для загрузки товаров из API Ozon.
Параметры:

load_products: Загрузить товары из базы данных (true/false).
limit: Количество товаров для загрузки.

update: Обновить товары (true/false).
WebSocket :
Уведомления о завершении задач через WebSocket.
URL: /ws/task-status/<task_id>/.

Swagger-документация :
Автоматически генерируемая OpenAPI-документация доступна по адресу /swagger/.

Админ-панель Django :
Управление данными через стандартную админ-панель Django: /admin/.

## 🔧 Примененные технологии

Backend - Django REST Framework (DRF) - Обработка API-запросов
База данных - PostgreSQL - Хранение данных о товарах
Асинхронность - Celery + Redis  - Выполнение долгих задач и WebSocket
Кэширование -  Redis  - Оптимизация повторных запросов
Сериализация - DRF Serializers - Валидация и преобразование данных
Документация - drf-yasg Swagger UI для API
Фронтенд - React.js - Интерфейс для тестирования API и отображения

## 🚀 Алгоритм запуска
1. Предварительные требования
Docker и Docker Compose установлены на вашей системе.



#### Собрать и запустить контейнеры :

docker-compose up --build

#### Применить миграции (в новом терминале):

docker-compose exec backend python manage.py migrate

#### Создать суперпользователя (опционально) :

docker-compose exec backend python manage.py createsuperuser

#### Собрать статику :

docker-compose exec backend python manage.py collectstatic

### Проверка работы

После запуска сервисы будут доступны:

API
http://localhost:8000/api/products/

Swagger
http://localhost:8000/swagger/

Админка
http://localhost:8000/admin/

Frontend
http://localhost:3000/


📂 Структура проекта
ozon-api-integration/
├── backend/             # Backend на Django
│   ├── api/             # Логика API (views, serializers, tasks)
│   ├── settings.py      # Настройки Django
│   ├── asgi.py          # Конфигурация ASGI
│   └── manage.py        # Управление Django
├── frontend/            # Frontend на React.js
│   ├── src/             # Исходный код React
│   └── package.json     # Зависимости React
├── docker-compose.yml   # Конфигурация Docker Compose
└── README.md            # Документация проекта

🎉 Итог
Проект готов к работе! 🚀

Backend : http://localhost:8000
Frontend : http://localhost:3000
Swagger : http://localhost:8000/swagger/