import django_filters

from .models import Task
from rest_framework.exceptions import ParseError
from .utils import TITLE_NAMES


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=[(0, '0'), (1, '1'), (2, '2')])
    title = django_filters.CharFilter(method='filter_by_title')

    class Meta:
        model = Task
        fields = ['status', 'title']
        
    def filter_by_title(self, queryset, name, value):
        if value == "visa":
            return queryset.filter(**{name + '__contains': value})
        if ' ' in value:
            raise ParseError("Spaces are not allowed in the title filter.")
        value = value.replace('-', ' ')
        if value not in TITLE_NAMES:
            raise ParseError("Invalid title.")
        return queryset.filter(**{name + '__exact': value})
