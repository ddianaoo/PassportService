from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .forms import UserRegisterForm, UserLoginForm


def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Успішна реєстрація!')
            return redirect('home')
        else:
            messages.error(request, form.errors)
    else:
        form = UserRegisterForm()
    return render(request, 'authentication/signup.html', {'form': form, 'title': 'Реєстрація'})


def signin(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Успішний вхід!')
                return redirect('home')
            else:
                messages.error(request, 'Невірний email або пароль.')
        else:
            messages.error(request, 'Помилка у формі. Будь ласка, перевірте введені дані.')
    else:
        form = UserLoginForm()
    return render(request, 'authentication/signin.html', {'form': form, 'title': 'Вхід'})


def signout(request):
    logout(request)
    return redirect('home')
