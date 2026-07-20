from django.core.exceptions import ValidationError


def validate_image_file(value):
    max_size = 5 * 1024 * 1024

    if value.size > max_size:
        raise ValidationError(
            f"Image file size must not exceed 5 MB. "
            f"Current size: {value.size / (1024 * 1024):.1f} MB"
        )

    valid_mime_types = ["image/jpeg", "image/png"]
    if hasattr(value, "content_type") and value.content_type not in valid_mime_types:
        raise ValidationError(
            f"Unsupported image format. Allowed: JPEG, PNG. Got: {value.content_type}"
        )
