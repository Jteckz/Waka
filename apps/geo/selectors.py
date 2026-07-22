from django.db.models import ExpressionWrapper, F, FloatField, Value
from django.db.models.functions import ASin, Cos, Power, Radians, Sin, Sqrt


def nearby(queryset, point, radius_km, lat_field="latitude", lng_field="longitude"):
    """Filter and order a queryset by proximity to a ``point`` (lat, lng).

    Uses the haversine formula computed in-database via Django ORM
    expressions (works on SQLite and PostgreSQL).  Returns a QuerySet
    annotated with ``distance`` (km) filtered to records within
    ``radius_km`` and ordered by distance ascending.
    """
    origin_lat, origin_lng = point
    if origin_lat is None or origin_lng is None:
        return queryset.none()

    lat1_rad = Radians(Value(origin_lat))
    lat2_rad = Radians(F(lat_field))
    dlat_rad = Radians(F(lat_field) - Value(origin_lat))
    dlng_rad = Radians(F(lng_field) - Value(origin_lng))

    a = Power(Sin(dlat_rad / 2), 2) + Cos(lat1_rad) * Cos(lat2_rad) * Power(
        Sin(dlng_rad / 2), 2
    )
    c = 2 * ASin(Sqrt(a))

    earth_radius_km = 6371.0
    distance_expr = ExpressionWrapper(
        Value(earth_radius_km) * c,
        output_field=FloatField(),
    )

    return (
        queryset.annotate(distance=distance_expr)
        .filter(distance__lte=radius_km)
        .order_by("distance")
    )
