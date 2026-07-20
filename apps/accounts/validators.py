from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class LetterDigitPasswordValidator:
    def validate(self, password, user=None):
        if not any(c.isalpha() for c in password):
            raise ValidationError(
                _("Password must contain at least one letter."),
                code="password_no_letter",
            )
        if not any(c.isdigit() for c in password):
            raise ValidationError(
                _("Password must contain at least one digit."),
                code="password_no_digit",
            )

    def get_help_text(self):
        return _("Your password must contain at least one letter and one digit.")
