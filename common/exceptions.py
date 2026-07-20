import re

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


class DomainError(Exception):
    code = "domain_error"
    message = "A domain error occurred"

    def __init__(self, message=None, details=None):
        self.message = message or self.message
        self.details = details or {}
        super().__init__(self.message)

    def to_envelope(self):
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


class PermissionDeniedError(DomainError):
    code = "permission_denied"
    message = "You do not have permission to perform this action"


class ValidationError(DomainError):
    code = "validation_error"
    message = "Validation failed"


class NotFoundError(DomainError):
    code = "not_found"
    message = "The requested resource was not found"


class OutOfServiceRadiusError(DomainError):
    code = "out_of_service_radius"
    message = "The agent is outside the serviceable radius"


class InvalidStateTransitionError(DomainError):
    code = "invalid_state_transition"
    message = "The requested state transition is not allowed"


_EXCEPTION_STATUS_MAP = {
    PermissionDeniedError: status.HTTP_403_FORBIDDEN,
    ValidationError: status.HTTP_400_BAD_REQUEST,
    NotFoundError: status.HTTP_404_NOT_FOUND,
    OutOfServiceRadiusError: status.HTTP_400_BAD_REQUEST,
    InvalidStateTransitionError: status.HTTP_409_CONFLICT,
}


def _camel_to_snake(name):
    s1 = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s2 = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s1)
    return s2.replace("__", "_").lower()


def _normalize_response(response, exc):
    if response is None:
        return response
    if "error" not in response.data:
        detail = response.data
        code = _camel_to_snake(type(exc).__name__)
        message = (
            str(detail)
            if isinstance(detail, str)
            else str(getattr(response, "status_text", "Error"))
        )
        response.data = {
            "error": {
                "code": code,
                "message": message,
                "details": detail if isinstance(detail, dict) else {},
            }
        }
    return response


def custom_exception_handler(exc, context):
    if isinstance(exc, DomainError):
        status_code = _EXCEPTION_STATUS_MAP.get(
            type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return Response(exc.to_envelope(), status=status_code)

    response = drf_exception_handler(exc, context)

    return _normalize_response(response, exc)
