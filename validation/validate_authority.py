from django.core.exceptions import ValidationError


def validate_authority(authority: int):
    if not 1111 < authority < 9999:
        raise ValidationError("Authority must be in the format xxxx.")
