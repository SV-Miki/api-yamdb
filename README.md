# YaMDb API

YaMDb - сервис для сбора отзывов пользователей на произведения (книги, фильмы, музыка).
Сами произведения в сервисе не хранятся - только каталог, отзывы, комментарии и пользовательские оценки, из которых считается рейтинг произведения.

## Возможности
* Регистрация пользователей и получение JWT-токена (/auth/signup/, /auth/token/)
* Управление пользователями (CRUD доступен админу), профиль текущего пользователя (/users/, /users/me/)
* Каталог произведений: категории, жанры, произведения (/categories/, /genres/, /titles/)
* Отзывы к произведениям и комментарии к отзывам (вложенные эндпоинты)
* Импорт данных из CSV (python manage.py import_csv)

## Технологии
* Python 3.x
* Django
* Django REST Framework (DRF)
* Simple JWT (djangorestframework-simplejwt)
* SQLite (по умолчанию)

## Установка и запуск

```bash
git clone https://github.com/SV-Miki/api-yamdb.git
cd api-yamdb


python -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Документация (ReDoc)

После запуска сервера откройте:
`http://127.0.0.1:8000/redoc/`

## Импорт тестовых данных из CSV

CSV лежат в `api_yamdb/static/data/`.

```bash
python manage.py import_csv
```

## Примеры запросов

1) Регистрация (получить confirmation_code на email)

`POST /api/v1/auth/signup/`

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","email":"user1@example.com"}'
  ```

Ответ:

```json
{"email":"user1@example.com","username":"user1"}
```

2) Получение JWT-токена

`POST /api/v1/auth/token/`

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","confirmation_code":"<CODE_FROM_EMAIL>"}'
```

Ответ:

```json
{"token":"<JWT_TOKEN>"}
```

3) Получить список категорий (публично)

`GET /api/v1/categories/`

```bash
curl -s http://127.0.0.1:8000/api/v1/categories/
```

Ответ:

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {"name": "Фильм", "slug": "movie"}
  ]
}
```

4) Создать жанр (только админ)

`POST /api/v1/genres/`

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/genres/ \
  -H "Authorization: Bearer <ADMIN_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Драма","slug":"drama"}'
  ```

Ответ:

```json
{"name":"Драма","slug":"drama"}
```


5) Создать отзыв на произведение (только авторизованный пользователь)

`POST /api/v1/titles/<title_id>/reviews/`

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/titles/1/reviews/ \
  -H "Authorization: Bearer <USER_JWT>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Отличное произведение!","score":10}'
  ```

Ответ:

```json
{
  "id": 1,
  "text": "Отличное произведение!",
  "author": "user1",
  "score": 10,
  "pub_date": "2025-12-26T00:00:00Z"
}
```

## Статус
Проект успешно проходит все автотесты pytest и все проверки из Postman-коллекции Ymdb-collection.postman_collection.json.

## Автор
#### Шилов Владислав Валерьевич
Студент 1 курса магистратуры ИТМО, направление "Фронтенд- и бэкенд-разработка".
