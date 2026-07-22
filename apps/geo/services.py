from geopy.distance import geodesic

from common.exceptions import OutOfServiceRadiusError


def _point(lat, lng):
    """Return a (lat, lng) tuple usable by geopy."""
    return (lat, lng)


def calculate_distance_km(point_a, point_b):
    """Return the geodesic distance in km between two (lat, lng) tuples."""
    return geodesic(point_a, point_b).kilometers


def is_within_radius(point_a, point_b, radius_km):
    return calculate_distance_km(point_a, point_b) <= radius_km


def validate_within_service_radius(origin_point, target_point, radius_km):
    if not is_within_radius(origin_point, target_point, radius_km):
        raise OutOfServiceRadiusError(
            f"Distance {calculate_distance_km(origin_point, target_point):.2f}km "
            f"exceeds service radius {radius_km}km"
        )
