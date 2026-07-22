from common.exceptions import ValidationError


def validate_latitude(lat):
    if not isinstance(lat, int | float):
        raise ValueError("Latitude must be a number")
    if lat < -90 or lat > 90:
        raise ValidationError(f"Latitude {lat} is out of range (-90 to 90)")


def validate_longitude(lng):
    if not isinstance(lng, int | float):
        raise ValueError("Longitude must be a number")
    if lng < -180 or lng > 180:
        raise ValidationError(f"Longitude {lng} is out of range (-180 to 180)")
