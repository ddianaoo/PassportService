from django.core.exceptions import ValidationError


def validate_number(number: int):
    if not 10000000 < number < 99999999:
        raise ValidationError("Document number must be in the format xxxxxxxx.")
