import pytest
from django.contrib.auth import get_user_model

from common.pagination import StandardCursorPagination, StandardPageNumberPagination


class TestStandardPageNumberPagination:
    def test_page_size_default(self):
        paginator = StandardPageNumberPagination()
        assert paginator.page_size == 20

    def test_max_page_size(self):
        paginator = StandardPageNumberPagination()
        assert paginator.max_page_size == 100

    def test_page_size_query_param(self):
        paginator = StandardPageNumberPagination()
        assert paginator.page_size_query_param == "page_size"

    @pytest.mark.django_db
    def test_paginates_queryset(self):
        user_model = get_user_model()
        for i in range(25):
            user_model.objects.create(
                phone=f"+255712{i:06d}", password="testpass1", role="MASTER_AGENT"
            )

        paginator = StandardPageNumberPagination()
        request = type("Request", (), {"query_params": {}})()
        qs = user_model.objects.all().order_by("id")
        page = paginator.paginate_queryset(qs, request)

        assert len(page) == 20

    @pytest.mark.django_db
    def test_respects_page_size_query_param(self):
        user_model = get_user_model()
        for i in range(30):
            user_model.objects.create(
                phone=f"+255713{i:06d}", password="testpass1", role="MASTER_AGENT"
            )

        paginator = StandardPageNumberPagination()
        request = type("Request", (), {"query_params": {"page_size": "5"}})()
        qs = user_model.objects.all().order_by("id")
        page = paginator.paginate_queryset(qs, request)

        assert len(page) == 5


class TestStandardCursorPagination:
    def test_ordering(self):
        paginator = StandardCursorPagination()
        assert paginator.ordering == "-created_at"

    def test_page_size_default(self):
        paginator = StandardCursorPagination()
        assert paginator.page_size == 20
