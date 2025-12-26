from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Пагинация по страницам для эндпоинтов API."""

    page_size = 10
