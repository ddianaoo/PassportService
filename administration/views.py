from authentication.forms import ReadOnlyUserForm
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from passports.models import Passport, ForeignPassport
from random import randint
import datetime
from .forms import PassportForm, ForeignPassportForm, RestorePassportForm


def get_tasks(request):
    if request.user.is_staff:
        tasks = Task.objects.all().order_by('-created_at', 'status')
        return render(request, 'administration/task_list.html', {'tasks': tasks, 'title': 'Список заявок'})
    messages.error(request, 'Дана сторінка недоступна.')
    return redirect('home')


def create_passport(request, pk):
    # add permissions
    task = get_object_or_404(Task, pk=pk)
    if task.status or task.user.passport:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')

    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365)
    passport = Passport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=randint(1111, 9999)
    )
    if request.method == 'POST':
        user_form = ReadOnlyUserForm(instance=task.user)
        form = PassportForm(request.POST, request.FILES, instance=passport)
        if form.is_valid():
            p = form.save()
            task.user.passport = p
            task.user.save()
            task.status = 1
            task.save()
            messages.success(request, 'Успішно оформлено внутрішній паспорт!')
            return redirect('tasks_list')
        else:
            messages.error(request, form.errors)
    user_form = ReadOnlyUserForm(instance=task.user)
    form = PassportForm(instance=passport)
    return render(request, 'administration/task_form.html',
                  {'form': form, 'user_form': user_form, 'title': 'Оформлення паспорту'})


def create_fpassport(request, pk):
    # add permissions
    task = get_object_or_404(Task, pk=pk)
    if task.status or task.user.foreign_passport:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')
    authority=task.user.passport.authority
    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365)
    passport = ForeignPassport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=authority
    )
    if request.method == 'POST':
        user_form = ReadOnlyUserForm(instance=task.user)
        form = ForeignPassportForm(request.POST, request.FILES, instance=passport)
        if form.is_valid():
            fp = form.save()
            task.user.foreign_passport = fp
            task.user.save()
            task.status = 1
            task.save()
            messages.success(request, 'Успішно оформлено закордонний паспорт!')
            return redirect('tasks_list')
        else:
            messages.error(request, form.errors)
    form = ForeignPassportForm(instance=passport)
    user_form = ReadOnlyUserForm(instance=task.user)
    return render(request, 'administration/task_form.html',
                  {'form': form, 'user_form': user_form, 'title': 'Оформлення паспорту'})



def restore_passport(request, pk):
    # add permissions
    task = get_object_or_404(Task, pk=pk)
    if task.status:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')
    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365)
    new_passport = Passport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=randint(1111, 9999)
    )
    if request.method == 'POST':
        user_form = ReadOnlyUserForm(instance=task.user)
        form = RestorePassportForm(request.POST, request.FILES, instance=new_passport)
        if form.is_valid():
            task.user.passport.delete()
            p = form.save()
            task.user.passport = p
            task.user.save()
            task.status = 1
            task.save()
            messages.success(request, 'Успішно відновлено внутрішній паспорт!')
            return redirect('tasks_list')
        else:
            messages.error(request, form.errors)
    form = RestorePassportForm(instance=new_passport)
    user_form = ReadOnlyUserForm(instance=task.user)
    return render(request, 'administration/task_form.html',
                  {'form': form, 'user_form': user_form, 'title': 'Відновлення паспорту'})

