from administration.models import Task
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskFilter
from rest_framework.generics import ListAPIView
from .serializers import TaskSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from passports.serializers import CreateInternalPassportSerializer, CreateForeignPassportSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from passports.models import Passport, ForeignPassport, Visa
from .views import create_passport
from rest_framework.permissions import IsAdminUser


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
    permission_classes = [IsAdminUser]


class CreateInternalPassportByStaffAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        if task.status or task.user.passport:
            return Response(
                {"detail": "Request has already been processed or the user already has a passport."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        passport = Passport(photo=task.user_data.get('photo'))
        serializer = CreateInternalPassportSerializer(instance=passport, 
                                              data=request.data, 
                                              context={'request': request})
        if serializer.is_valid():
            serializer.save()
            task.user.passport = passport
            task.user.save()
            task.status = 1
            task.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RestoreInternalPassportAPIView(APIView):    
    permission_classes = [IsAdminUser]

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        if task.status:
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        passport = create_passport(task, Passport)
        serializer = CreateInternalPassportSerializer(instance=passport, 
                                                      data=request.data,
                                                      context={'request': request})
        
        if serializer.is_valid():
            task.user.passport.delete()
            task.user.passport = serializer.save()
            task.user.save()
            task.status = 1
            task.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CreateForeignPassportForUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        if task.status or task.user.foreign_passport:
            return Response(
                {"detail": "Request has already been processed or the user already has a foreign passport."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        passport = ForeignPassport(photo=task.user_data.get('photo'))
        serializer = CreateForeignPassportSerializer(instance=passport, 
                                                     data=request.data, 
                                                     context={'request': request})
        if serializer.is_valid():
            serializer.save()
            task.user.foreign_passport = passport
            task.user.save()
            task.status = 1
            task.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RestoreForeignPassportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        if task.status:
            return Response(
                {"detail": "This user's request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        passport = ForeignPassport(photo=task.user_data.get('photo')) 
        serializer = CreateForeignPassportSerializer(instance=passport, 
                                                     data=request.data, 
                                                     context={'request': request})

        if serializer.is_valid():
            visas = Visa.objects.filter(foreign_passport=task.user.foreign_passport)
            visas.delete()

            task.user.foreign_passport.delete()
            task.user.foreign_passport = serializer.save()
            task.user.save()

            task.status = 1
            task.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
