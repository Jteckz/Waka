import django
from django.conf import settings


class TestSettings:
    def test_django_setup_succeeds(self):
        django.setup()

    def test_expected_third_party_apps_are_installed(self):
        required_apps = [
            "rest_framework",
            "corsheaders",
            "drf_spectacular",
            "django_filters",
        ]
        for app in required_apps:
            assert app in settings.INSTALLED_APPS, f"{app} missing from INSTALLED_APPS"
