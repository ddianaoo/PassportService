import datetime
from django.core.exceptions import ValidationError


def validate_expiry_date(expiry_date):
    today = datetime.date.today()
    if today > expiry_date:
        raise ValidationError("Expiry date must be at least in 4 years(for children) and 10(for adults).")