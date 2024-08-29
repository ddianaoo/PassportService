import re
from django.core.exceptions import ValidationError


def validate_record_number(record_number:str):
    if not re.match(r'^\d{8}-\d{5}$', record_number):
        raise ValidationError("Record number must be in the format xxxxxxxx-xxxxx.")