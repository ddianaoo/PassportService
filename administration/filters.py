import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=[(0, '0'), (1, '1')])
    title = django_filters.CharFilter(method='filter_by_title')

    class Meta:
        model = Task
        fields = ['status', 'title']
        
    def filter_by_title(self, queryset, name, value):
        if ' ' in value:
            return queryset.none()
        value = value.replace('-', ' ')
        return queryset.filter(**{name + '__exact': value})
