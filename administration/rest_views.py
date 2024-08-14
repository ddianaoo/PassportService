from administration.models import Task
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TaskFilter
from .serializers import TaskSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from passports.serializers import CreateInternalPassportSerializer, CreateForeignPassportSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from passports.models import Address, Passport, ForeignPassport, Visa
from rest_framework.permissions import IsAdminUser


class TaskListAPIView(ReadOnlyModelViewSet):
    queryset = Task.objects.all().order_by('-created_at', 'status')
    serializer_class = TaskSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter
    permission_classes = [IsAdminUser]


class CreateInternalPassportByStaffAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, task_pk):
        task_title = "create an internal passport"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
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
        task_title = "restore an internal passport"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title not in task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        passport = Passport(photo=task.user_data.get('photo'))
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
        task_title = "create a foreign passport"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
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
        task_title = "restore a foreign passport"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title not in task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
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


class ChangeAddressForUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, task_pk):
        task_title = "change registation address"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response({"detail": "This user's request has already been processed."},
                            status=status.HTTP_400_BAD_REQUEST)
        address_id = task.user_data.get("address_id")
        if not address_id:
            return Response({"detail": "No address ID found in the task data."},
                            status=status.HTTP_400_BAD_REQUEST)

        addr = get_object_or_404(Address, pk=address_id)
        task.user.address = addr
        task.user.save()
        task.status = 1
        task.save()

        return Response({"detail": "The registration address has been successfully updated."},
                        status=status.HTTP_200_OK)
    

class ChangeUserFieldForUserAPIView(APIView):
    permission_classes = [IsAdminUser]

    def handle_user_field_update(self, task, passport_serializer, field_name, new_value, fpassport_serializer=None):
        task.user.passport.delete()
        setattr(task.user, field_name, new_value)
        task.user.passport = passport_serializer.save()

        if fpassport_serializer:
            Visa.objects.filter(foreign_passport=task.user.foreign_passport).delete()
            task.user.foreign_passport.delete()
            task.user.foreign_passport = fpassport_serializer.save()

        task.user.save()
        task.status = 1
        task.save()

        return Response({'detail': f'The user {field_name} has been successfully updated.'}, status=status.HTTP_200_OK)

    def put(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        if task.status:
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        for key in ['name', 'surname', 'patronymic']:
            new_value = task.user_data.get(key)
            if new_value:
                field_name = key
                break
        task_title = f"change user {field_name}"
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)

        new_ipassport = Passport(photo=task.user_data.get('photo')) 
        ipassport_serializer = CreateInternalPassportSerializer(instance=new_ipassport, 
                                                      data=request.data.get('internal_passport'),
                                                      context={'request': request})
        if not task.user.foreign_passport:
            if ipassport_serializer.is_valid():
                return self.handle_user_field_update(task, ipassport_serializer, field_name, new_value)
            return Response(ipassport_serializer.errors, status=status.HTTP_400_BAD_REQUEST)       

        new_fpassport = ForeignPassport(photo=task.user_data.get('photo')) 
        fpassport_serializer = CreateForeignPassportSerializer(instance=new_fpassport, 
                                                               data=request.data.get('foreign_passport'),
                                                               context={'request': request})
        if ipassport_serializer.is_valid() and fpassport_serializer.is_valid():
            return self.handle_user_field_update(task, ipassport_serializer, field_name, new_value, fpassport_serializer)
        
        errors = {}
        if not ipassport_serializer.is_valid():
            errors['internal_passport'] = ipassport_serializer.errors
        if not fpassport_serializer.is_valid():
            errors['foreign_passport'] = fpassport_serializer.errors

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

