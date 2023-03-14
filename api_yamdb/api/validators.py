import datetime

from django.core.exceptions import ValidationError


def year_validator(year):
    if year > datetime.datetime.now().year:
        raise ValidationError(
            'Должен быть текущий год.'
        )
