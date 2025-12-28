from rest_framework.pagination import PageNumberPagination

from api_yamdb.constants import DEFAULT_PAGE_SIZE


class DefaultPagination(PageNumberPagination):
    """Пагинация по страницам для эндпоинтов API."""

    page_size = DEFAULT_PAGE_SIZE
