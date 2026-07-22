import pytest
from django.db import connection, models

from apps.geo.models import GeoLocatedModel
from apps.geo.selectors import nearby


class _TestLocation(GeoLocatedModel):
    name = models.CharField(max_length=50)

    class Meta:
        app_label = "geo"


@pytest.fixture(scope="module")
def create_test_table(django_db_blocker, django_db_setup):
    with django_db_blocker.unblock(), connection.schema_editor() as schema_editor:
        schema_editor.create_model(_TestLocation)
    yield


@pytest.mark.usefixtures("create_test_table")
@pytest.mark.django_db
class TestNearby:
    def setup_method(self):
        self.origin = (-6.8130, 39.2880)

    def test_returns_nearby_points(self):
        _TestLocation.objects.create(
            name="Mlimani City", latitude=-6.7820, longitude=39.2650
        )
        _TestLocation.objects.create(
            name="Kariakoo", latitude=-6.8190, longitude=39.2780
        )
        _TestLocation.objects.create(
            name="Bagamoyo", latitude=-6.4330, longitude=38.9000
        )

        qs = nearby(_TestLocation.objects.all(), self.origin, 10)
        names = list(qs.values_list("name", flat=True))
        assert len(names) == 2
        assert "Mlimani City" in names
        assert "Kariakoo" in names
        assert "Bagamoyo" not in names

    def test_orders_by_distance_ascending(self):
        _TestLocation.objects.create(name="Far", latitude=-6.8190, longitude=39.2780)
        _TestLocation.objects.create(name="Near", latitude=-6.8120, longitude=39.2890)

        qs = nearby(_TestLocation.objects.all(), self.origin, 10)
        names = list(qs.values_list("name", flat=True))
        assert names[0] == "Near"
        assert names[1] == "Far"

    def test_annotates_distance(self):
        _TestLocation.objects.create(name="Test", latitude=-6.7820, longitude=39.2650)
        obj = nearby(_TestLocation.objects.all(), self.origin, 10).first()
        assert obj.distance is not None
        assert obj.distance > 0

    def test_empty_queryset_when_origin_none(self):
        qs = nearby(_TestLocation.objects.all(), (None, None), 10)
        assert qs.count() == 0
