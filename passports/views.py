from administration.models import Task
import datetime
from django.contrib import messages
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AddressForm, PhotoForm
from .models import Address


def main_page(request):
    return render(request, 'home.html')


def create_passport(request):
    task = Task.objects.filter(user=request.user, title="Create ip", status=0).exists()
    if task:
        messages.error(request, 'Ви вже відправили заявку на створення внутрішнього паспорту.')
        return redirect('get_documents')
    if request.user.passport:
        messages.error(request, 'Ви вже маєте внутрішній паспорт.')
        return redirect('get_documents')

    if request.method == 'POST':
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
    return render(request, 'passports/create_passport.html', {'address_form': address_form, 
                                                              'photo_form': photo_form, 
                                                              'title': 'Заявка на створення паспорту'})


def get_documents(request):
    return render(request, 'passports/get_documents.html', {'passport': request.user.passport,
                                                            'foreign_passport': request.user.foreign_passport,
                                                            'user': request.user})