import datetime

from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination

from administration.models import Task
from administration.filters import TaskFilter
from authentication.serializers import (
    ChangeUserDataSerializer,
    UserListSerializer
)
from .models import Visa
from .serializers import (
    AddressSerializer,
    PhotoSerializer,
    RetrieveDocumentsSerializer,
    RetrieveInternalPassportSerializer,
    RetrieveForeignPassportSerializer,
    RestorePassportSerializer,
    VisaSerializer,
    CreateVisaSerializer,
    ExtendVisaSerializer
)
from .views import get_photo_path, get_address
from .permissions import IsClient
from administration.serializers import TaskSerializer


class CustomPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 100


class InternalPassportDetailAPIView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        passport = request.user.passport
        if passport:
            user_serializer = RetrieveInternalPassportSerializer(passport, context={'request': request})
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Internal passport not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        task_title = "create an internal passport"

        if Task.objects.filter(user=user, title=task_title, status=0).exists():
            return Response({"detail": "You have already sent a request for creating an internal passport."},
                            status=status.HTTP_400_BAD_REQUEST)
        if user.passport:
            return Response({"detail": "You already have an internal passport."},
                            status=status.HTTP_400_BAD_REQUEST)

        address_serializer = AddressSerializer(data=request.data)
        photo_serializer = PhotoSerializer(data=request.data)
        is_address_valid = address_serializer.is_valid()
        is_photo_valid = photo_serializer.is_valid()

        if is_address_valid and is_photo_valid:
            adr, created = get_address(address_serializer.validated_data)
            photo = photo_serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)
            user_data = {'photo': photo_path, 'address_id': adr.pk}
            Task.objects.create(user=user, title=task_title, user_data=user_data)
            return Response({"detail": "Your request for creating an internal passport has been sent."},
                            status=status.HTTP_201_CREATED)
        else:
            errors = {}
            if not is_address_valid:
                errors["address_errors"] = address_serializer.errors
            if not is_photo_valid:
                errors["photo_errors"] = photo_serializer.errors

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user

        serializer = RestorePassportSerializer(data=request.data)
        if serializer.is_valid():
            task_reason = serializer.validated_data.get('reason')
            task_title = f"restore an internal passport due to {task_reason}"

            if Task.objects.filter(user=user, title=task_title, status=0).exists():
                return Response({"detail": f"You have already sent a request for restoring an internal passport due to {task_reason}."},
                                status=status.HTTP_400_BAD_REQUEST)
            if not user.passport:
                return Response({"detail": "You don't have an internal passport yet."},
                                status=status.HTTP_400_BAD_REQUEST)

            photo = serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)
            Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})
            return Response({"detail": f"Your request for restoring an internal passport due to {task_reason} has been sent."},
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForeignPassportDetailAPIView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        foreign_passport = request.user.foreign_passport
        if foreign_passport:
            user_serializer = RetrieveForeignPassportSerializer(foreign_passport, context={'request': request})
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "You don`t have a foreign passport yet."}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        task_title = "create a foreign passport"

        if Task.objects.filter(user=user, title=task_title, status=0).exists():
            return Response({"detail": "You have already sent a request for creating a foreign passport."},
                            status=status.HTTP_400_BAD_REQUEST)
        if user.foreign_passport:
            return Response({"detail": "You already have a foreign passport."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not user.passport:
            return Response({"detail": "You must have an internal passport to create a foreign passport."},
                            status=status.HTTP_400_BAD_REQUEST)

        photo_serializer = PhotoSerializer(data=request.data)
        if photo_serializer.is_valid():
            photo = photo_serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)
            Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})
            return Response({"detail": "Your request for creating a foreign passport has been sent."},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        user = request.user

        serializer = RestorePassportSerializer(data=request.data)
        if serializer.is_valid():
            task_reason = serializer.validated_data.get('reason')
            task_title = f"restore a foreign passport due to {task_reason}"

            if Task.objects.filter(user=user, title=task_title, status=0).exists():
                return Response({"detail": f"You have already sent a request for restoring a foreign passport due to {task_reason}."},
                                status=status.HTTP_400_BAD_REQUEST)
            if not user.foreign_passport:
                return Response({"detail": "You don't have a foreign passport yet."},
                                status=status.HTTP_400_BAD_REQUEST)

            photo = serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)
            Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})
            return Response({"detail": f"Your request for restoring a foreign passport due to {task_reason} has been sent."},
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetDocumentsAPIView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        user_serializer = RetrieveDocumentsSerializer(request.user, context={'request': request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class UserAddressAPIView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        address = request.user.address
        if address:
            user_serializer = AddressSerializer(address, context={'request': request})
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "You don`t have a registration address yet."}, status=status.HTTP_200_OK)

    def patch(self, request):
        task_title = 'change registation address'

        if Task.objects.filter(user=request.user, title=task_title, status=0).exists():
            return Response({"detail": "You have already submitted a request to update your registration address."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not request.user.passport:
            return Response({"detail": "You do not have a passport, so updating the address is not possible."},
                            status=status.HTTP_400_BAD_REQUEST)

        address_serializer = AddressSerializer(data=request.data)

        if address_serializer.is_valid():
            adr, created = get_address(address_serializer.validated_data)
            Task.objects.create(user=request.user, title=task_title, user_data={'address_id': adr.pk})
            return Response({"detail": "Your request to update the registration address has been submitted."},
                            status=status.HTTP_200_OK)
        else:
            return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDataAPIView(APIView):
    permission_classes = [IsClient]

    def get(self, request):
        user_serializer = UserListSerializer(request.user)
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        user = request.user
        if not user.passport:
            return Response({"detail": "You must have an internal passport to change the data."},
                            status=status.HTTP_400_BAD_REQUEST)

        user_serializer = ChangeUserDataSerializer(data=request.data)
        photo_serializer = PhotoSerializer(data=request.data)
        is_user_valid = user_serializer.is_valid()
        is_photo_valid = photo_serializer.is_valid()

        if is_user_valid and is_photo_valid:
            field = user_serializer.validated_data.get('field')
            task_title = f"change user {field}"
            if Task.objects.filter(user=user, title=task_title, status=0).exists():
                return Response({"detail": f"You have already sent a request for changing the {field}."},
                                status=status.HTTP_400_BAD_REQUEST)

            value = user_serializer.validated_data.get('value')
            photo = photo_serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)
            user_data = {'photo': photo_path, field: value}
            Task.objects.create(user=user, title=task_title, user_data=user_data)
            return Response({"detail": f"Your request for changing the {field} has been sent."},
                            status=status.HTTP_200_OK)
        else:
            errors = {}
            if not is_user_valid:
                errors["user_errors"] = user_serializer.errors
            if not is_photo_valid:
                errors["photo_errors"] = photo_serializer.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class VisaViewSet(ViewSet):
    permission_classes = [IsClient]

    def get_queryset(self, request):
        return Visa.objects.filter(foreign_passport=request.user.foreign_passport, is_active=True).order_by('-is_active')

    def list(self, request):
        serializer = VisaSerializer(self.get_queryset(request), many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        item = get_object_or_404(self.get_queryset(request), pk=pk)
        serializer = VisaSerializer(item, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        task_title = "create a visa"
        if not user.foreign_passport:
            return Response({"detail": "You must have a foreign passport to create a visa."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = CreateVisaSerializer(data=request.data)
        if serializer.is_valid():
            visa_type = serializer.validated_data.get('type')
            country = serializer.validated_data.get('country')
            entry_amount = serializer.validated_data.get('entry_amount')
            check_task = Task.objects.filter(
                user=user,
                title=task_title,
                status=0,
                user_data__visa_country=country
            )
            if check_task.exists():
                return Response(
                    {"detail": f"You have already sent a request for creating a visa of {country}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            old_visa = Visa.objects.filter(
                foreign_passport=user.foreign_passport,
                type=visa_type,
                country=country,
                entry_amount=entry_amount,
                is_active=True
            )
            if old_visa.exists() and old_visa.get().date_of_expiry > datetime.date.today() + datetime.timedelta(days=30):
                return Response(
                    {"detail": f"You have already have a visa of {country}."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            photo = serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title, 'visas')
            user_data = {'photo': photo_path, 'visa_country': country, 'visa_type': visa_type, 'visa_entry_amount': entry_amount}
            Task.objects.create(user=user, title=task_title, user_data=user_data)
            return Response({"detail": "Your request for creating a visa has been sent."},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        user = request.user
        task_title = "extend a visa"
        visa = get_object_or_404(self.get_queryset(request), pk=pk)
        if not visa.is_active:
            return Response({"detail": "Only an active visa can be extended."},
                            status=status.HTTP_400_BAD_REQUEST)
        if Task.objects.filter(user=user, title=task_title, status=0, user_data__visa_id=pk).exists():
            return Response({"detail": f"You have already sent a request for extending a visa of {visa.country}."},
                            status=status.HTTP_400_BAD_REQUEST)

        visa_serializer = ExtendVisaSerializer(data=request.data)
        if visa_serializer.is_valid():
            reason = visa_serializer.validated_data.get('reason')
            extension_date = visa_serializer.validated_data.get('extension_date')
            if extension_date <= visa.date_of_expiry:
                return Response(
                    {"detail": "The extension date must be greater than the expiration date."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user_data = {'visa_id': pk, 'visa_extension_reason': reason, 'visa_extension_date': str(extension_date)}
            Task.objects.create(user=user, title=task_title, user_data=user_data)
            return Response({"detail": "Your request for extending a visa has been sent."},
                            status=status.HTTP_200_OK)
        else:
            return Response(visa_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        user = request.user
        task_title = "restore a visa due to loss"
        visa = get_object_or_404(self.get_queryset(request), pk=pk)
        if not visa.is_active:
            return Response({"detail": "Only an active visa can be restored."},
                            status=status.HTTP_400_BAD_REQUEST)
        if Task.objects.filter(user=user, title=task_title, status=0, user_data__visa_id=pk).exists():
            return Response({"detail": f"You have already sent a request for restoring a visa of {visa.country}."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = PhotoSerializer(data=request.data)
        if serializer.is_valid():
            photo = serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title, 'visas')
            Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path, 'visa_id': pk})
            return Response({"detail": "Your request for restoring a visa due to loss has been sent."},
                            status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskListForUserViewSet(ReadOnlyModelViewSet):
    queryset = Task.objects.all().order_by('status', '-created_at')
    serializer_class = TaskSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TaskFilter
    permission_classes = [IsClient]
    pagination_class = CustomPagination

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).order_by('status', '-created_at')

    def list(self, request, *args, **kwargs):
        page = request.query_params.get('page')
        if page == 'all':
            queryset = self.filter_queryset(self.get_queryset())
            count = len(queryset)
            serializer = self.get_serializer(queryset, many=True)
            return Response({'count': count, 'tasks': serializer.data})
        else:
            return super().list(request, *args, **kwargs)
