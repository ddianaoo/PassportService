
import datetime
from django.core.exceptions import ValidationError


def validate_birth_date(birth_date):
    today = datetime.date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    if age < 14:
        raise ValidationError("You must be at least 14 years old.")
