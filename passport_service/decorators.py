from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


def client_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            messages.error(request, 'Ви зайшли з акаунту робітника, який немає таких прав.')
            return redirect(reverse('home'))
        elif request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect(reverse('signin'))
    return wrapper
