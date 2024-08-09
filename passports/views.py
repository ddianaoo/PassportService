from administration.models import Task
from authentication.forms import UpdateUserNameForm, UpdateUserSurnameForm, UpdateUserPatronymicForm
import datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from .forms import AddressForm, PhotoForm
from .models import Address
import uuid
from passport_service.decorators import client_login_required


def main_page(request):
    return render(request, 'home.html')


@client_login_required
def get_documents(request):
    return render(request, 'passports/get_documents.html', {'user': request.user})


def get_photo_path(photo, user, task_title):
    """
    Generate a unique file path for the user's photo, incorporating a UUID to ensure uniqueness.

    Args:
        photo: The uploaded photo file.
        user (models.Model): The user object, used to get user-specific details.
        task_title (str): The title of the task, used in the file name.

    Returns:
        str: The generated file path where the photo will be saved.
    """
    today = datetime.date.today()
    month = f'{today.month:02d}'
    day = f'{today.day:02d}'
    task_title = task_title.replace(" ", "-")
    unique_id = uuid.uuid4().hex
    extension = photo.name.split(".")[-1]
    photo_name = f'{user.id}-{user.surname}-{user.name}-{task_title}-{unique_id}.{extension}'
    photo_path = default_storage.save(f'photos/passports/{today.year}/{month}/{day}/{photo_name}', photo)  
    return photo_path  


def get_address(address_form):
    """
    Retrieve or create an address based on the provided form data.

    Args:
        address_form: The form containing the address fields.

    Returns:
        Tuple[models.Model, bool]: The Address object and a boolean indicating whether it was created.
    """
    country_code = address_form.cleaned_data.get('country_code')
    region = address_form.cleaned_data.get('region')
    settlement = address_form.cleaned_data.get('settlement')
    street = address_form.cleaned_data.get('street')
    apartments = address_form.cleaned_data.get('apartments')
    post_code = address_form.cleaned_data.get('post_code')
    adr, created = Address.objects.get_or_create(country_code=country_code, region=region, settlement=settlement, 
                                         street=street, apartments=apartments, post_code=post_code)
    return adr, created


@client_login_required
def create_passport(request):
    task_title = "create an internal passport"
    user = request.user
    task = Task.objects.filter(user=user, title=task_title, status=0).exists()
    if task:
        messages.error(request, 'Ви вже відправили заявку на створення внутрішнього паспорту.')
        return redirect('get_documents')
    if user.passport:
        messages.error(request, 'Ви вже маєте внутрішній паспорт.')
        return redirect('get_documents')

    if request.method == 'POST':
        photo_form = PhotoForm(request.POST, request.FILES)       
        address_form = AddressForm(request.POST)

        if address_form.is_valid() and photo_form.is_valid():
            adr, created = get_address(address_form)
            request.user.address = adr
            request.user.save()
            photo = photo_form.cleaned_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)
            task = Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})        
            messages.success(request, 'Ваша заява на створення внутрішнього паспорту відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, address_form.errors)
            messages.error(request, photo_form.errors)
    else:
        address_form = AddressForm()
        photo_form = PhotoForm()
    return render(request, 'passports/create_passport.html', {'address_form': address_form, 
                                                              'photo_form': photo_form, 
                                                              'title': 'Заява на створення паспорту'})


@client_login_required
def create_fpassport(request):
    task_title = "create a foreign passport"
    user = request.user
    task = Task.objects.filter(user=user, title=task_title, status=0).exists()
    if task:
        messages.error(request, 'Ви вже відправили заявку на створення закордонного паспорту.')
        return redirect('get_documents')
    if request.user.foreign_passport:
        messages.error(request, 'Ви вже маєте закордонний паспорт.')
        return redirect('get_documents')
    if not user.passport:
        messages.error(request, 'Для створення закордонного паспорту необхідно мати внутрішній паспорт.')
        return redirect('get_documents')        

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)       
        if form.is_valid():
            photo = form.cleaned_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)   
            task = Task.objects.create(user=user, title=task_title, user_data={'photo': photo_path})        
            messages.success(request, 'Ваша заявка на створення закордонного паспорту відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, form.errors)
    else:
        form = PhotoForm()
    return render(request, 'passports/index_form.html', { 'form': form, 'user': user, 'create_fpassport': True,
                                                        'title': 'Заявка на створення закордонного паспорту'})


@client_login_required
def restore_passport(request, title, error_msg):
    user = request.user
    task = Task.objects.filter(user=user, title=title, status=0).exists()
    if task:
        messages.error(request, error_msg)
        return redirect('get_documents')
    if not user.passport:
        messages.error(request, 'У вас ще нема паспорту.')
        return redirect('get_documents')        

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)       
        if form.is_valid():
            photo = form.cleaned_data.get('photo')
            photo_path = get_photo_path(photo, user, title)   
            task = Task.objects.create(user=user, title=title, user_data={'photo': photo_path})        
            messages.success(request, 'Ваша заява на відновлення внутрішнього паспотру відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, form.errors)
    else:
        form = PhotoForm()
    return render(request, 'passports/index_form.html', { 'form': form, 'user': user,
                                                              'title': 'Заява на відновлення внутрішнього паспотру'})


@client_login_required
def restore_passport_loss(request):
    return restore_passport(request, "restore an internal passport due to loss", 
                     'Ви вже відправили заявку на відновлення внутрішнього паспотру через втрату.')


@client_login_required
def restore_passport_expiry(request):
    return restore_passport(request, "restore an internal passport due to expiry",
                     'Ви вже відправили заяву на відновлення внутрішнього паспотру через закінчення терміну придатності.')


@client_login_required
def restore_fpassport(request,  title, error_msg):
    user = request.user
    task = Task.objects.filter(user=user, title=title, status=0).exists()
    if task:
        messages.error(request, error_msg)
        return redirect('get_documents')
    if not user.foreign_passport:
        messages.error(request, 'У вас ще нема закордонного паспорту.')
        return redirect('get_documents')        

    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)       
        if form.is_valid():
            photo = form.cleaned_data.get('photo')
            photo_path = get_photo_path(photo, user, title)  
            task = Task.objects.create(user=user, title=title, user_data={'photo': photo_path})        
            messages.success(request, 'Ваша заяка на відновлення закордонного паспотру відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, form.errors)
    else:
        form = PhotoForm()
    return render(request, 'passports/index_form.html', { 'form': form, 'user': user,
                                                              'title': 'Заява на відновлення закордонного паспотру'})


@client_login_required
def restore_fpassport_loss(request):
    return restore_fpassport(request, "restore a foreign passport due to loss",
                     'Ви вже відправили заяву на відновлення закордонного паспотру через втрату.')


@client_login_required
def restore_fpassport_expiry(request):
    return restore_fpassport(request, "restore a foreign passport due to expiry",
                     'Ви вже відправили заяву на відновлення закордонного паспотру через закінчення терміну придатності.')


@client_login_required
def change_address(request):
    task_title = 'change registation address'
    task = Task.objects.filter(user=request.user, title=task_title, status=0).exists()
    if task:
        messages.error(request, 'Ви вже відправили заяву на оновлення адреси прописки.')
        return redirect('get_documents')
    if not request.user.passport:
        messages.error(request, 'У вас ще нема паспорту, тому неможливе оновлення адреси прописки.')
        return redirect('get_documents')  
    
    if request.method == 'POST':     
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            adr, created = get_address(address_form)
            task = Task.objects.create(user=request.user, title=task_title, user_data={'address_id': adr.pk})        
            messages.success(request, 'Ваша заява на оновлення адреси прописки відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, address_form.errors)
    else:
        address_form = AddressForm()
    return render(request, 'passports/update_address_form.html', {'form': address_form, 
                                                              'title': 'Заява на оновлення адреси прописки'})


def change_data(request, task_title, UserDataForm, field):
    user = request.user
    task = Task.objects.filter(user=user, title=task_title, status=0).exists()
    if task:
        messages.error(request, 'Ви вже відправили заяву на оновлення даних паспорту.')
        return redirect('get_documents')
    if not user.passport:
        messages.error(request, 'У вас ще нема паспорту, тому неможливе оновлення ваших даних.')
        return redirect('get_documents')  
    
    if request.method == 'POST':     
        photo_form = PhotoForm(request.POST, request.FILES) 
        user_form = UserDataForm(request.POST, instance=user)

        if user_form.is_valid() and photo_form.is_valid():
            field_value = user_form.cleaned_data.get(field)
            photo = photo_form.cleaned_data.get('photo')
            photo_path = get_photo_path(photo, user, task_title)       
            task = Task.objects.create(user=request.user, title=task_title, user_data={'photo': photo_path, field: field_value})        
            messages.success(request, 'Ваша заява на оновлення даних паспорту відправлена!')
            return redirect('get_documents')
        else:
            messages.error(request, user_form.errors)
            messages.error(request, photo_form.errors)
    else:
        user_form = UserDataForm(instance=user)
        photo_form = PhotoForm()
    return render(request, 'passports/update_data_form.html', {'user_form': user_form, 'photo_form': photo_form,
                                                              'title': 'Заява на оновлення даних паспорту'})    


@client_login_required
def change_name(request):
    return change_data(request, "change user name", UpdateUserNameForm, 'name')


@client_login_required
def change_surname(request):
    return change_data(request, "change user surname", UpdateUserSurnameForm, 'surname')


@client_login_required
def change_patronymic(request):
    return change_data(request, "change user patronymic", UpdateUserPatronymicForm, 'patronymic')

