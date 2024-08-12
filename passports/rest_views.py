from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AddressCreateSerializer, PhotoSerializer
from administration.models import Task
from .views import get_photo_path, get_address 


class CreatePassportAPIView(APIView):
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
        

        

