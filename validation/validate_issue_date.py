import datetime
from django.core.exceptions import ValidationError


def validate_issue_date(issue_date):
    today = datetime.date.today()
    if today > issue_date:
        raise ValidationError("Issue date must be at least today.")