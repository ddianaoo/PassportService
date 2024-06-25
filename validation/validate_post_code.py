from django.core.exceptions import ValidationError


def validate_post_code(number: int):
    if not 10000 < number < 99999:
        raise ValidationError("Post code must be in the format xxxxx.")
    