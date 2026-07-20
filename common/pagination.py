from rest_framework.pagination import CursorPagination, PageNumberPagination


class StandardCursorPagination(CursorPagination):
    ordering = "-created_at"
    page_size = 20


class StandardPageNumberPagination(PageNumberPagination):
    page_size = 20
    max_page_size = 100
    page_size_query_param = "page_size"
