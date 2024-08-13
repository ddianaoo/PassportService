from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
    AddressCreateSerializer, 
    PhotoSerializer, 
    DocumentsRetrieveSerializer, 
    PassportRetrieveSerializer,
    ForeignPassportRetrieveSerializer
)
from administration.models import Task
from .views import get_photo_path, get_address 


class InternalPassportDetailAPIView(APIView):
    def get(self, request):
        passport = request.user.passport
        if passport:
            user_serializer = PassportRetrieveSerializer(passport, context={'request': request})
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Internal passport not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user = request.user
        task_title = "create an internal passport"
        
        if Task.objects.filter(user=user, title=task_title, status=0).exists():
            return Response({"detail": "You have already sent an application for the creation of an internal passport."},
                            status=status.HTTP_400_BAD_REQUEST)
        if user.passport:
            return Response({"detail": "You already have an internal passport."},
                            status=status.HTTP_400_BAD_REQUEST)
        
        address_serializer = AddressCreateSerializer(data=request.data)
        photo_serializer = PhotoSerializer(data=request.data)
        is_address_valid = address_serializer.is_valid()
        is_photo_valid = photo_serializer.is_valid()
        
        if is_address_valid and is_photo_valid:
            adr, created = get_address(address_serializer.validated_data)
            request.user.address = adr
            request.user.save()

            photo = photo_serializer.validated_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)

            task = Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})
            
            return Response({"detail": "Your request for creating an internal passport has been sent."},
                            status=status.HTTP_201_CREATED)
        else:
            errors = {}
            if not is_address_valid:
                errors["address_errors"] = address_serializer.errors
            if not is_photo_valid:
                errors["photo_errors"] = photo_serializer.errors
                
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        

class ForeignPassportDetailAPIView(APIView):
    def get(self, request):
        foreign_passport = request.user.foreign_passport
        if foreign_passport:
            user_serializer = ForeignPassportRetrieveSerializer(foreign_passport, context={'request': request})
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Foreign passport not found."}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request):
        user = request.user
        task_title = "create a foreign passport"

        if Task.objects.filter(user=user, title=task_title, status=0).exists():
            return Response({"detail": "You have already sent an application for creating a foreign passport."},
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
            return Response({"detail": "Your application for creating a foreign passport has been sent."},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)        


class GetDocumentsAPIView(APIView):
    def get(self, request):
        user_serializer = DocumentsRetrieveSerializer(request.user, context={'request': request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)
    