import pytest

from apps.geo.utils import validate_latitude, validate_longitude
from common.exceptions import ValidationError


class TestCoordinateValidation:
    def test_valid_latitude(self):
        assert validate_latitude(0) is None

    def test_valid_longitude(self):
        assert validate_longitude(0) is None

    def test_rejects_latitude_out_of_range(self):
        with pytest.raises(ValidationError):
            validate_latitude(100)

    def test_rejects_longitude_out_of_range(self):
        with pytest.raises(ValidationError):
            validate_longitude(200)

    def test_rejects_non_numeric_latitude(self):
        with pytest.raises(ValueError):
            validate_latitude("abc")

    def test_edge_cases(self):
        validate_latitude(-90)
        validate_latitude(90)
        validate_longitude(-180)
        validate_longitude(180)
