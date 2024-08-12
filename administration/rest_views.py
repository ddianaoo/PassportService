from administration.models import Task
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskFilter
from rest_framework.generics import ListAPIView
from .serializers import TaskSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet


# class TaskListAPIView(ListAPIView):
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filterset_class = TaskFilter

class TaskListAPIView(ReadOnlyModelViewSet):
    queryset = Task.objects.all().order_by('-created_at', 'status')
    serializer_class = TaskSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter

