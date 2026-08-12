# YaMDb API

YaMDb - REST API для сервиса отзывов на произведения: книги, фильмы, музыку и другие категории.

Сами произведения в сервисе не хранятся. API предоставляет каталог произведений, категории и жанры, отзывы пользователей, комментарии к отзывам и рейтинг произведений, рассчитанный на основе пользовательских оценок.

## Возможности

- регистрация пользователей и получение JWT-токена
- ролевая модель пользователей: `user`, `moderator`, `admin`
- управление пользователями администратором
- просмотр и редактирование собственного профиля через `/users/me/`
- работа с категориями, жанрами и произведениями
- фильтрация произведений по названию, году, категории и жанру
- публикация отзывов и комментариев
- автоматический расчёт рейтинга произведения по оценкам пользователей
- разграничение прав доступа для обычных пользователей, модераторов и администраторов
- импорт подготовленных данных из CSV
- документация API в формате ReDoc

## Технологии

- Python 3.12
- Django 6.0
- Django REST Framework 3.15.2
- django-filter 25.2
- djangorestframework-simplejwt 5.4.0
- SQLite
- pytest
- flake8

## Структура проекта

```text
api-yamdb/
├── api_yamdb/
│   ├── api/
│   │   ├── v1/                         # API v1: views, serializers, permissions, filters
│   │   │   ├── filters.py
│   │   │   ├── pagination.py
│   │   │   ├── permissions.py
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── apps.py
│   │   └── urls.py                     # Подключение маршрутов API
│   ├── api_yamdb/                      # Конфигурация Django-проекта
│   │   ├── constants.py                # Общие константы проекта
│   │   ├── settings.py                 # Настройки Django
│   │   ├── urls.py                     # Корневые URL-маршруты
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── reviews/                        # Произведения, категории, жанры, отзывы и комментарии
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── import_csv.py       # Импорт данных из CSV
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py                   # Модели предметной области
│   │   └── services.py                 # Вспомогательные функции
│   ├── users/                          # Пользовательская модель, роли и валидация
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   └── validators.py
│   ├── static/
│   │   ├── data/                       # Подготовленные CSV-данные для импорта
│   │   │   ├── category.csv
│   │   │   ├── comments.csv
│   │   │   ├── genre.csv
│   │   │   ├── genre_title.csv
│   │   │   ├── review.csv
│   │   │   ├── titles.csv
│   │   │   └── users.csv
│   │   └── redoc.yaml                  # OpenAPI-спецификация
│   ├── templates/
│   │   └── redoc.html                  # Страница документации ReDoc
│   └── manage.py                       # CLI Django
├── postman_collection/                 # Postman-коллекция для проверки API
│   ├── README.md
│   ├── set_up_data.sh
│   └── Ymdb-collection.postman_collection.json
├── tests/                              # Набор автотестов pytest
│   ├── fixtures/
│   ├── conftest.py
│   ├── test_00_user_registration.py
│   ├── test_01_users.py
│   ├── test_02_category.py
│   ├── test_03_genre.py
│   ├── test_04_title.py
│   ├── test_05_review.py
│   ├── test_06_comment.py
│   ├── test_07_files.py
│   └── utils.py
├── .env.example                        # Пример переменных окружения
├── .gitignore
├── LICENSE
├── pytest.ini                          # Конфигурация pytest
├── README.md
├── requirements.txt                    # Зависимости проекта
└── setup.cfg                           # Конфигурация flake8
```

## Основные эндпоинты

- `POST /api/v1/auth/signup/` — регистрация пользователя и отправка `confirmation_code`
- `POST /api/v1/auth/token/` — получение JWT-токена
- `/api/v1/users/` — управление пользователями
- `/api/v1/users/me/` — профиль текущего пользователя
- `/api/v1/categories/` — категории
- `/api/v1/genres/` — жанры
- `/api/v1/titles/` — произведения
- `/api/v1/titles/{title_id}/reviews/` — отзывы
- `/api/v1/titles/{title_id}/reviews/{review_id}/comments/` — комментарии к отзывам

## Установка и запуск

Клонируйте репозиторий:

```bash
git clone https://github.com/SV-Miki/api-yamdb.git
cd api-yamdb
```

Создайте и активируйте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate
```

Для Windows:

```bash
venv\Scripts\activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

### Переменные окружения

Пример используемых переменных находится в `.env.example`:

```env
DJANGO_SECRET_KEY=replace_with_a_random_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Проект использует переменные окружения через `os.getenv()`. Файл `.env.example` служит примером конфигурации и автоматически не загружается.

Для локального запуска можно экспортировать переменные в shell:

```bash
export DJANGO_SECRET_KEY='your-secret-key'
export DJANGO_DEBUG='True'
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
```

Если переменные не заданы, используются значения по умолчанию из `settings.py`.

Примените миграции:

```bash
python api_yamdb/manage.py migrate
```

При необходимости создайте суперпользователя:

```bash
python api_yamdb/manage.py createsuperuser
```

Запустите сервер:

```bash
python api_yamdb/manage.py runserver
```

После запуска API будет доступен по адресу `http://127.0.0.1:8000/`.

## Документация API

ReDoc доступен после запуска сервера:

`http://127.0.0.1:8000/redoc/`

## Импорт данных из CSV

Подготовленные CSV-файлы находятся в:

`api_yamdb/static/data/`

Импортируются пользователи, категории, жанры, произведения, связи произведений с жанрами, отзывы и комментарии.

Запуск импорта:

```bash
python api_yamdb/manage.py import_csv
```

## Примеры запросов

### Регистрация пользователя

`POST /api/v1/auth/signup/`

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@example.com"}'
```

Пример ответа:

```json
{
  "email": "user1@example.com",
  "username": "user1"
}
```

`confirmation_code` отправляется на email пользователя. В локальной конфигурации Django используется консольный email backend, поэтому письмо выводится в терминал, где запущен сервер.

### Получение JWT-токена

`POST /api/v1/auth/token/`

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","confirmation_code":"<CODE_FROM_EMAIL>"}'
```

Пример ответа:

```json
{
  "token": "<JWT_TOKEN>"
}
```

### Получение списка категорий

`GET /api/v1/categories/`

```bash
curl -s http://127.0.0.1:8000/api/v1/categories/
```

Пример ответа:

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "name": "Фильм",
      "slug": "movie"
    }
  ]
}
```

### Создание жанра

Доступно только администратору.

`POST /api/v1/genres/`

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/genres/ \
  -H "Authorization: Bearer <ADMIN_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Драма","slug":"drama"}'
```

Пример ответа:

```json
{
  "name": "Драма",
  "slug": "drama"
}
```

### Создание отзыва

Доступно авторизованному пользователю. Один пользователь может оставить только один отзыв на произведение.

`POST /api/v1/titles/{title_id}/reviews/`

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/titles/1/reviews/ \
  -H "Authorization: Bearer <USER_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Отличное произведение!","score":10}'
```

Пример ответа:

```json
{
  "id": 1,
  "text": "Отличное произведение!",
  "author": "user1",
  "score": 10,
  "pub_date": "2026-01-01T12:00:00Z"
}
```

## Тестирование и проверка кода

Запуск автотестов:

```bash
pytest
```

Проверка стиля:

```bash
flake8
```

Проверка конфигурации Django:

```bash
python api_yamdb/manage.py check
```

## Автор

Владислав Шилов
