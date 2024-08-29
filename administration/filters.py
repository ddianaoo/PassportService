import django_filters

from .models import Task
from rest_framework.exceptions import ParseError
from .utils import TITLE_NAMES_AND_SLUGS


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=[(0, '0'), (1, '1')])
    title = django_filters.ChoiceFilter(method='filter_by_title', choices=TITLE_NAMES_AND_SLUGS)

    class Meta:
        model = Task
        fields = ['status', 'title']
        
    def filter_by_title(self, queryset, name, value):
        if ' ' in value:
            raise ParseError("Spaces are not allowed in the title filter.")
        value = value.replace('-', ' ')
        return queryset.filter(**{name + '__exact': value})
