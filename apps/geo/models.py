from django.db import models

from apps.geo.utils import validate_latitude, validate_longitude


class GeoLocatedModel(models.Model):
    """
    Abstract model storing lat/lng as FloatFields.

    GDAL/PostGIS PointField is not used here because GDAL is not guaranteed
    to be available in all environments (e.g., CI, local dev). The FloatField
    approach uses geopy for all distance calculations and works everywhere.
    Production deployment with PostGIS can override or extend with a
    computed Point column.
    """

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True

    def set_coordinates(self, lat, lng):
        validate_latitude(lat)
        validate_longitude(lng)
        self.latitude = lat
        self.longitude = lng
