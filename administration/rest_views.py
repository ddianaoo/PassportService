from datetime import date

from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from administration.models import Task
from .filters import TaskFilter
from .serializers import TaskUserSerializer
from passports.serializers import (CreateInternalPassportSerializer, 
                                   CreateForeignPassportSerializer, 
                                   VisaSerializer,
                                   RestoreVisaSerializer)
from passports.models import Address, Passport, ForeignPassport, Visa


class TaskListAPIView(ReadOnlyModelViewSet):
    queryset = Task.objects.all().order_by('status', '-created_at')
    serializer_class = TaskUserSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter
    permission_classes = [IsAdminUser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        page = request.query_params.get('page')
        if page == 'all':
            queryset = self.filter_queryset(self.get_queryset())
            count = len(queryset)
            serializer = self.get_serializer(queryset, many=True)
            return Response({'count': count, 'tasks': serializer.data})
        else:
            return super().list(request, *args, **kwargs)    


class CreateInternalPassportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, task_pk):
        task_title = "create an internal passport"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        passport = Passport(photo=task.user_data.get("photo"))
        serializer = CreateInternalPassportSerializer(instance=passport, 
                                              data=request.data, 
                                              context={'request': request})
        if serializer.is_valid():
            task.user.address = get_object_or_404(Address, pk=task.user_data.get("address_id"))
            serializer.save()
            task.user.passport = passport
            task.user.save()
            task.status = 1
            task.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RestoreInternalPassportAPIView(APIView):    
    permission_classes = [IsAdminUser]

    def put(self, request, task_pk):
        task_titles = ["restore an internal passport due to loss", "restore an internal passport due to expiry"]
        task = get_object_or_404(Task, pk=task_pk)
        if task.title not in task_titles:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        passport = Passport(photo=task.user_data.get("photo"))
        serializer = CreateInternalPassportSerializer(
            instance=passport, 
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            task.user.passport.delete()
            task.user.passport = serializer.save()
            task.user.save()
            task.status = 1
            task.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CreateForeignPassportAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, task_pk):
        task_title = "create a foreign passport"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        passport = ForeignPassport(photo=task.user_data.get("photo"))
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

    def put(self, request, task_pk):
        task_titles = ["restore a foreign passport due to loss", "restore a foreign passport due to expiry"]
        task = get_object_or_404(Task, pk=task_pk)
        if task.title not in task_titles:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response(
                {"detail": "This user's request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        passport = ForeignPassport(photo=task.user_data.get("photo")) 
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

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserAddressAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, task_pk):
        task_title = "change registation address"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response({"detail": "This user's request has already been processed."},
                            status=status.HTTP_400_BAD_REQUEST)        

        addr = get_object_or_404(Address, pk=task.user_data.get("address_id"))
        task.user.address = addr
        task.user.save()
        task.status = 1
        task.save()

        return Response({"detail": "The registration address has been successfully updated."},
                        status=status.HTTP_200_OK)
    

class ChangeUserFieldAPIView(APIView):
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

    def patch(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        if task.status:
            return Response(
                {"detail": "This user's request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        field_name = ''
        for key in ['name', 'surname', 'patronymic']:
            new_value = task.user_data.get(key)
            if new_value:
                field_name = key
                break
        task_title = f"change user {field_name}"
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)           
        
        new_ipassport = Passport(photo=task.user_data.get("photo")) 
        ipassport_serializer = CreateInternalPassportSerializer(instance=new_ipassport, 
                                                      data=request.data.get('internal_passport'),
                                                      context={'request': request})
        if not task.user.foreign_passport:
            if ipassport_serializer.is_valid():
                return self.handle_user_field_update(task, ipassport_serializer, field_name, new_value)
            return Response(ipassport_serializer.errors, status=status.HTTP_400_BAD_REQUEST)       

        new_fpassport = ForeignPassport(photo=task.user_data.get("photo")) 
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


class CreateVisaAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, task_pk):
        task_title = "create a visa"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        visa = Visa(
            photo=task.user_data.get("photo"),
            type=task.user_data.get("visa_type"),
            country=task.user_data.get("visa_country"),
            entry_amount=task.user_data.get("visa_entry_amount"),
            foreign_passport=task.user.foreign_passport
        )
        serializer = VisaSerializer(
            instance=visa, 
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            old_visa = Visa.objects.filter(
                foreign_passport=task.user.foreign_passport,
                type=visa.type, 
                country=visa.country, 
                entry_amount=visa.entry_amount,
                is_active=True
            ).first()
            if old_visa:
                old_visa.is_active = False
                old_visa.save()
            serializer.save()
            task.status = 1
            task.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExtendVisaExtentionAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, task_pk):
        task_title = "extend a visa"
        task = get_object_or_404(Task, pk=task_pk)
        if task_title != task.title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        visa = Visa.objects.get(pk=task.user_data.get("visa_id"))
        visa.date_of_expiry = date.fromisoformat(task.user_data.get("visa_extension_date"))
        visa.save()
        task.status = 1
        task.save()
        return Response({"detail": "You successfully accepted the visa extension."}, status=status.HTTP_200_OK)
    

class RejectTaskAPIView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        if task.status in (1, 2):
            return Response(
                {"detail": "Request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        task.status = 2
        task.save()
        return Response(
            {"detail": f"You successfully rejected the request `{task.title}` by {task.user.surname} {task.user.name} user."},
             status=status.HTTP_200_OK)
    

class RestoreVisaAPIView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, task_pk):
        task_title = "restore a visa due to loss"
        task = get_object_or_404(Task, pk=task_pk)
        if task.title != task_title:
            return Response({"detail": "The task with this id and title wasn`t found."}, 
                            status=status.HTTP_404_NOT_FOUND)
        if task.status:
            return Response(
                {"detail": "This user's request has already been processed."},
                status=status.HTTP_400_BAD_REQUEST
            )
        old_visa = Visa.objects.get(pk=task.user_data.get("visa_id"))
        visa = Visa(
            photo=task.user_data.get("photo"),
            type=old_visa.type,
            country=old_visa.country,
            entry_amount=old_visa.entry_amount,
            foreign_passport=task.user.foreign_passport,
            date_of_expiry=old_visa.date_of_expiry
        ) 
        serializer = RestoreVisaSerializer(
            instance=visa, 
            data=request.data, 
            context={'request': request}
        )
        if serializer.is_valid():
            old_visa.is_active = False
            old_visa.save()
            serializer.save()
            task.status = 1
            task.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

