from administration.models import Task
from authentication.forms import ReadOnlyUserForm
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from .forms import AddressForm, PhotoForm
from .models import Address


def main_page(request):
    return render(request, 'home.html')


@login_required
def create_passport(request):
    task = Task.objects.filter(user=request.user, title="Create ip", status=0).exists()
    if task:
        messages.error(request, 'Ви вже відправили заявку на створення внутрішнього паспорту.')
        return redirect('get_documents')
    if request.user.passport:
        messages.error(request, 'Ви вже маєте внутрішній паспорт.')
        return redirect('get_documents')

    if request.method == 'POST':
        user_form = ReadOnlyUserForm(instance=request.user)
        photo_form = PhotoForm(request.POST, request.FILES)       
        address_form = AddressForm(request.POST)

        if address_form.is_valid() and photo_form.is_valid():
            country_code = address_form.cleaned_data.get('country_code')
            region = address_form.cleaned_data.get('region')
            settlement = address_form.cleaned_data.get('settlement')
            street = address_form.cleaned_data.get('street')
            apartments = address_form.cleaned_data.get('apartments')
            post_code = address_form.cleaned_data.get('post_code')

            adr, created = Address.objects.get_or_create(country_code=country_code, region=region, settlement=settlement, 
                                         street=street, apartments=apartments, post_code=post_code)
            request.user.address = adr
            request.user.save()

            photo = photo_form.cleaned_data.get('photo')
            today = datetime.date.today()
            month = f'{today.month:02d}'
            day = f'{today.day:02d}'
            photo_name = f'{request.user.pk}-{request.user.name}-{request.user.surname}-passport.{photo.name.split(".")[-1]}'
            photo_path = default_storage.save(f'photos/passports/{today.year}/{month}/{day}/{photo_name}', photo)    

            task = Task.objects.create(user=request.user,title='Create ip', user_data={'photo': photo_path})        
            messages.success(request, 'Ваша заявка на створення внутрішнього паспорту відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, address_form.errors)
            messages.error(request, photo_form.errors)
    else:
        address_form = AddressForm()
        photo_form = PhotoForm()
        user_form = ReadOnlyUserForm(instance=request.user)
    return render(request, 'passports/create_passport.html', {'address_form': address_form, 
                                                              'photo_form': photo_form, 
                                                              'user_form': user_form,
                                                              'title': 'Заявка на створення паспорту'})


@login_required
def create_fpassport(request):
    task = Task.objects.filter(user=request.user, title="Create fp", status=0).exists()
    if task:
        messages.error(request, 'Ви вже відправили заявку на створення закордонного паспорту.')
        return redirect('get_documents')
    if request.user.foreign_passport:
        messages.error(request, 'Ви вже маєте закордонний паспорт.')
        return redirect('get_documents')
    if not request.user.passport:
        messages.error(request, 'Для створення закордонного паспорту необхідно мати внутрішній паспорт.')
        return redirect('get_documents')        

    if request.method == 'POST':
        user_form = ReadOnlyUserForm(instance=request.user)
        form = PhotoForm(request.POST, request.FILES)       
        if form.is_valid():
            photo = form.cleaned_data.get('photo')
            today = datetime.date.today()
            month = f'{today.month:02d}'
            day = f'{today.day:02d}'
            photo_name = f'{request.user.pk}-{request.user.name}-{request.user.surname}-fpassport.{photo.name.split(".")[-1]}'
            photo_path = default_storage.save(f'photos/passports/{today.year}/{month}/{day}/{photo_name}', photo)    

            task = Task.objects.create(user=request.user,title='Create fp', user_data={'photo': photo_path})        
            messages.success(request, 'Ваша заявка на створення закордонного паспорту відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, form.errors)
    else:
        user_form = ReadOnlyUserForm(instance=request.user)
        form = PhotoForm()
    return render(request, 'passports/index_form.html', { 'form': form, 
                                                               'user_form': user_form,
                                                              'title': 'Заявка на створення закордонного паспорту'})

@login_required
def get_documents(request):
    return render(request, 'passports/get_documents.html', {'passport': request.user.passport,
                                                            'foreign_passport': request.user.foreign_passport,
                                                            'user': request.user})


@login_required
def restore_passport(request, title, reason, error_msg):
    task = Task.objects.filter(user=request.user, title=title, status=0).exists()
    if task:
        messages.error(request, error_msg)
        return redirect('get_documents')
    if not request.user.passport:
        messages.error(request, 'У вас ще нема паспорту.')
        return redirect('get_documents')        

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)       
        user_form = ReadOnlyUserForm(instance=request.user)
        if form.is_valid():
            photo = form.cleaned_data.get('photo')
            today = datetime.date.today()
            month = f'{today.month:02d}'
            day = f'{today.day:02d}'
            photo_name = f'{request.user.pk}-{request.user.name}-{request.user.surname}-passport-{reason}.{photo.name.split(".")[-1]}'
            photo_path = default_storage.save(f'photos/passports/{today.year}/{month}/{day}/{photo_name}', photo)    

            task = Task.objects.create(user=request.user,title=title, user_data={'photo': photo_path})        
            messages.success(request, 'Ваша заявка на відновлення внутрішнього паспотру відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, form.errors)
    else:
        form = PhotoForm()
        user_form = ReadOnlyUserForm(instance=request.user)
    return render(request, 'passports/index_form.html', { 'form': form, 'user_form': user_form,
                                                              'title': 'Заявка на відновлення внутрішнього паспотру'})


@login_required
def restore_passport_loss(request):
    return restore_passport(request, "Restore ip - loss", 'loss', 
                     'Ви вже відправили заявку на відновлення внутрішнього паспотру через втрату.')


@login_required
def restore_passport_expiry(request):
    return restore_passport(request, "Restore ip - expiry", 'expiry', 
                     'Ви вже відправили заявку на відновлення внутрішнього паспотру через закінчення терміну придатності.')


@login_required
def restore_fpassport(request,  title, reason, error_msg):
    task = Task.objects.filter(user=request.user, title=title, status=0).exists()
    if task:
        messages.error(request, error_msg)
        return redirect('get_documents')
    if not request.user.foreign_passport:
        messages.error(request, 'У вас ще нема закордонного паспорту.')
        return redirect('get_documents')        

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)       
        user_form = ReadOnlyUserForm(instance=request.user)
        if form.is_valid():
            photo = form.cleaned_data.get('photo')
            today = datetime.date.today()
            month = f'{today.month:02d}'
            day = f'{today.day:02d}'
            photo_name = f'{request.user.pk}-{request.user.name}-{request.user.surname}-fpassport-{reason}.{photo.name.split(".")[-1]}'
            photo_path = default_storage.save(f'photos/passports/{today.year}/{month}/{day}/{photo_name}', photo)    

            task = Task.objects.create(user=request.user,title=title, user_data={'photo': photo_path})        
            messages.success(request, 'Ваша заявка на відновлення закордонного паспотру відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, form.errors)
    else:
        form = PhotoForm()
        user_form = ReadOnlyUserForm(instance=request.user)
    return render(request, 'passports/index_form.html', { 'form': form, 'user_form': user_form,
                                                              'title': 'Заявка на відновлення закордонного паспотру'})


@login_required
def restore_fpassport_loss(request):
    return restore_fpassport(request, "Restore fp - loss", 'loss', 
                     'Ви вже відправили заявку на відновлення закордонного паспотру через втрату.')


@login_required
def restore_fpassport_expiry(request):
    return restore_fpassport(request, "Restore fp - expiry", 'expiry', 
                     'Ви вже відправили заявку на відновлення закордонного паспотру через закінчення терміну придатності.')