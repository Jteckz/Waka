import pytest

from apps.geo.services import (
    calculate_distance_km,
    is_within_radius,
    validate_within_service_radius,
)
from common.exceptions import OutOfServiceRadiusError


class TestCalculateDistanceKm:
    def test_dar_to_dar(self):
        """Two known Dar es Salaam locations ~5km apart.

        (Posta, -6.8130, 39.2880) to (Mlimani City, -6.7820, 39.2650)
        is approximately 4.2 km per public map data.
        """
        posta = (-6.8130, 39.2880)
        mlimani = (-6.7820, 39.2650)
        dist = calculate_distance_km(posta, mlimani)
        assert 3.7 <= dist <= 4.7

    def test_same_point(self):
        p = (-6.8, 39.2)
        assert calculate_distance_km(p, p) == 0.0

    def test_known_distance(self):
        """Equator to North Pole ~10,000 km (quarter meridian)."""
        equator = (0.0, 0.0)
        north_pole = (90.0, 0.0)
        dist = calculate_distance_km(equator, north_pole)
        assert 9900 <= dist <= 10100


class TestIsWithinRadius:
    def test_within(self):
        a = (-6.8, 39.2)
        b = (-6.81, 39.21)
        assert is_within_radius(a, b, 5) is True

    def test_beyond(self):
        a = (-6.8, 39.2)
        b = (-6.9, 39.3)
        assert is_within_radius(a, b, 1) is False


class TestValidateWithinServiceRadius:
    def test_inside_passes(self):
        validate_within_service_radius((-6.8130, 39.2880), (-6.7820, 39.2650), 10)

    def test_outside_raises(self):
        with pytest.raises(OutOfServiceRadiusError):
            validate_within_service_radius((-6.8130, 39.2880), (-6.7820, 39.2650), 1)
