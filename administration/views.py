from authentication.forms import ReadOnlyUserForm
import datetime
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import Task
from passports.models import Passport, ForeignPassport
from random import randint
from .forms import PassportForm, ForeignPassportForm, RestorePassportForm


class TaskListView(ListView):
    model = Task
    context_object_name = 'tasks'
    paginate_by = 5
    template_name = 'administration/task_list.html'

    def get_queryset(self):
        title_filters = ('create-passport', 
                         'create-foreign-passport', 
                         'create-visa', 
                         'restore-passport-loss',
                         'restore-fpassport-loss',
                         'restore-passport-expiry',
                         'restore-fpassport-expiry',
                         'change-data'
                         )
        d = dict(zip(title_filters, Task.TITLE_CHOICES))
        tasks = Task.objects.all().order_by('-created_at', 'status')

        title = self.request.GET.get('title')
        if title and title in title_filters:
            tasks = tasks.filter(title=d[title][0])

        status = self.request.GET.get('status')
        if status:
            tasks = tasks.filter(status=status)
        
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список заявок'
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Дана сторінка недоступна.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


@staff_member_required(login_url='signin')
def create_passport(request, pk):
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


@staff_member_required(login_url='signin')
def create_fpassport(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Дана сторінка недоступна.')
        return redirect('home')
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


@staff_member_required(login_url='signin')
def restore_passport(request, pk):
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
            messages.success(request, 'Успішно поновлено внутрішній паспорт!')
            return redirect('tasks_list')
        else:
            messages.error(request, form.errors)
    form = RestorePassportForm(instance=new_passport)
    user_form = ReadOnlyUserForm(instance=task.user)
    return render(request, 'administration/task_form.html',
                  {'form': form, 'user_form': user_form, 'title': 'Поновлення паспорту'})

