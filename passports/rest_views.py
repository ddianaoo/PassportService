from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from administration.models import Task
from authentication.serializers import (
    ChangeUserDataSerializer,
    UserListSerializer
)
from .serializers import (
    CreateAddressSerializer, 
    PhotoSerializer, 
    RetrieveDocumentsSerializer, 
    RetrieveInternalPassportSerializer,
    RetrieveForeignPassportSerializer,
    RestorePassportSerializer,
    RetrieveAddressSerializer,
)
from .views import get_photo_path, get_address 
from .permissions import IsClient


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
        
        address_serializer = CreateAddressSerializer(data=request.data)
        photo_serializer = PhotoSerializer(data=request.data)
        is_address_valid = address_serializer.is_valid()
        is_photo_valid = photo_serializer.is_valid()
        
        if is_address_valid and is_photo_valid:
            adr, created = get_address(address_serializer.validated_data)
            photo = photo_serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)
            user_data = {'photo': photo_path, 'address_id': adr.pk}
            task = Task.objects.create(user=user, title=task_title, user_data=user_data)
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
            task = Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})
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
            return Response({"detail": "Foreign passport not found."}, status=status.HTTP_404_NOT_FOUND)
        
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
            task = Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})
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
            task = Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})
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
            user_serializer = RetrieveAddressSerializer(address, context={'request': request})
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Registration address not found."}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        task_title = 'change registation address'

        if Task.objects.filter(user=request.user, title=task_title, status=0).exists():
            return Response({"detail": "You have already submitted a request to update your registration address."},
                            status=status.HTTP_400_BAD_REQUEST)
        if not request.user.passport:
            return Response({"detail": "You do not have a passport, so updating the address is not possible."},
                            status=status.HTTP_400_BAD_REQUEST)

        address_serializer = CreateAddressSerializer(data=request.data)

        if address_serializer.is_valid():
            adr, created = get_address(address_serializer.validated_data)
            Task.objects.create(user=request.user, title=task_title, user_data={'address_id': adr.pk})   
            return Response({"detail": "Your request to update the registration address has been submitted."},
                            status=status.HTTP_200_OK)
        else:
            return Response(address_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangeUserDataAPIView(APIView):
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
            user_data={'photo': photo_path, field: value}
            task = Task.objects.create(user=user, title=task_title, user_data=user_data)
            return Response({"detail": f"Your request for changing the {field} has been sent."},
                            status=status.HTTP_200_OK)
        else:
            errors = {}
            if not is_user_valid:
                errors["user_errors"] = user_serializer.errors
            if not is_photo_valid:
                errors["photo_errors"] = photo_serializer.errors
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
