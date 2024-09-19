import datetime
from django.core.exceptions import ValidationError


def validate_expiry_date(expiry_date):
    ten_years_more = datetime.date.today() + datetime.timedelta(10 * 365 + 2)
    if ten_years_more > expiry_date:
        raise ValidationError("The expiry date must be in 10 years since today.")
