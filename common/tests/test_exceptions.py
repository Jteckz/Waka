import pytest
from rest_framework import status
from rest_framework.exceptions import NotFound as DRFNotFound
from rest_framework.exceptions import ValidationError as DRFValidationError

from common.exceptions import (
    DomainError,
    InvalidStateTransitionError,
    NotFoundError,
    OutOfServiceRadiusError,
    PermissionDeniedError,
    ValidationError,
    custom_exception_handler,
)


class TestDomainExceptions:
    def test_domain_error_defaults(self):
        exc = DomainError()
        envelope = exc.to_envelope()
        assert envelope["error"]["code"] == "domain_error"
        assert envelope["error"]["message"] == "A domain error occurred"
        assert envelope["error"]["details"] == {}

    def test_domain_error_custom_message(self):
        exc = DomainError(message="Custom message")
        assert exc.to_envelope()["error"]["message"] == "Custom message"

    def test_domain_error_custom_details(self):
        exc = DomainError(details={"field": "value"})
        assert exc.to_envelope()["error"]["details"] == {"field": "value"}

    def test_permission_denied_envelope(self):
        exc = PermissionDeniedError()
        envelope = exc.to_envelope()
        assert envelope["error"]["code"] == "permission_denied"

    def test_validation_error_envelope(self):
        exc = ValidationError()
        envelope = exc.to_envelope()
        assert envelope["error"]["code"] == "validation_error"

    def test_not_found_envelope(self):
        exc = NotFoundError()
        envelope = exc.to_envelope()
        assert envelope["error"]["code"] == "not_found"

    def test_out_of_service_radius_envelope(self):
        exc = OutOfServiceRadiusError()
        envelope = exc.to_envelope()
        assert envelope["error"]["code"] == "out_of_service_radius"

    def test_invalid_state_transition_envelope(self):
        exc = InvalidStateTransitionError()
        envelope = exc.to_envelope()
        assert envelope["error"]["code"] == "invalid_state_transition"

    def test_exception_is_an_exception(self):
        with pytest.raises(DomainError):
            raise PermissionDeniedError()
        with pytest.raises(DomainError):
            raise NotFoundError()


class TestCustomExceptionHandler:
    def test_handles_permission_denied_domain_error(self):
        exc = PermissionDeniedError(message="Access denied")
        response = custom_exception_handler(exc, {})
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"]["code"] == "permission_denied"
        assert response.data["error"]["message"] == "Access denied"

    def test_handles_validation_domain_error(self):
        exc = ValidationError(message="Invalid data")
        response = custom_exception_handler(exc, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_handles_not_found_domain_error(self):
        exc = NotFoundError(message="Resource not found")
        response = custom_exception_handler(exc, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_handles_out_of_service_radius_domain_error(self):
        exc = OutOfServiceRadiusError()
        response = custom_exception_handler(exc, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_handles_invalid_state_transition_domain_error(self):
        exc = InvalidStateTransitionError()
        response = custom_exception_handler(exc, {})
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_normalizes_drf_not_found(self):
        exc = DRFNotFound("Object not found")
        response = custom_exception_handler(exc, {})
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.data
        assert response.data["error"]["code"] == "not_found"

    def test_normalizes_drf_validation_error(self):
        exc = DRFValidationError({"email": ["This field is required."]})
        response = custom_exception_handler(exc, {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert response.data["error"]["code"] == "validation_error"
        assert response.data["error"]["details"] == {
            "email": ["This field is required."]
        }

    def test_returns_none_for_unhandled_exception(self):
        exc = ValueError("Something unexpected")
        response = custom_exception_handler(exc, {})
        assert response is None
