from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from passports.models import Passport
from random import randint
import datetime
from .forms import PassportForm


def get_tasks(request):
    if request.user.is_staff:
        tasks = Task.objects.all()
        return render(request, 'administration/task_list.html', {'tasks': tasks, 'title': 'Список заявок'})
    messages.error(request, 'Дана сторінка недоступна.')
    return redirect('home')


def create_passport(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.status or task.user.passport:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('home')
    record_number = task.user.date_of_birth.strftime('%Y%m%d') + f'-{randint(1, 99999):05d}'
    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365)
    passport = Passport(record_number=record_number, 
                        date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=randint(1111, 9999)
    )
    if request.method == 'POST':
        form = PassportForm(request.POST, request.FILES, instance=passport)
        if form.is_valid():
            p = form.save()
            task.user.passport = p
            task.user.save()
            task.status = 1
            task.save()
            messages.success(request, 'Успішно оформлено внутрішній паспорт!')
            return redirect('home')
        else:
            messages.error(request, form.errors)
    form = PassportForm(instance=passport)
    return render(request, 'administration/create_passport.html',
                  {'form': form, 'title': 'Оформлення паспорту'})

