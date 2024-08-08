import datetime
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import Task
from passports.models import Address, Passport, ForeignPassport, Visa
from random import randint
from passports.forms import PassportForm, ForeignPassportForm


class TaskListView(ListView):
    model = Task
    context_object_name = 'tasks'
    paginate_by = 5
    template_name = 'administration/task_list.html'
    title_filters = (
            'create-passport', 
            'create-foreign-passport', 
            'create-visa', 
            'restore-passport-loss', 
            'restore-fpassport-loss',
            'restore-passport-expiry', 
            'restore-fpassport-expiry', 
            'change-name', 
            'change-surname', 
            'change-patronymic', 
            'change-address', 
    )
    title_paths = (
            'create_passport_s',
            'create_fpassport_s',
            '',
            'restore_passport_s', 
            'restore_fpassport_s',
            'restore_passport_s',
            'restore_fpassport_s',
            'change_name_s', 
            'change_surname_s',
            'change_patronymic_s',
            'change_address_s'
    )

    def get_queryset(self):
        filters_dict = dict(zip(self.title_filters, Task.TITLE_CHOICES))
        tasks = Task.objects.all().order_by('-created_at', 'status')
        title = self.request.GET.get('title')

        if title and title in self.title_filters:
            tasks = tasks.filter(title=filters_dict[title][0])
        return tasks

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список заявок'
        paths_dict = dict(zip([i[0] for i in Task.TITLE_CHOICES], self.title_paths))
        tasks_with_addresses = []
        for task in context['tasks']:
            task.path = paths_dict[task.title]
            user_data = task.user_data
            if 'address_id' in user_data:
                try:
                    address = Address.objects.get(pk=user_data['address_id'])
                    formatted_address = f"{address.country_code}, {address.region}, {address.settlement}, {address.street}, {address.apartments}, {address.post_code}"
                    user_data['formatted_address'] = formatted_address
                except Address.DoesNotExist:
                    user_data['formatted_address'] = 'Неможливо визначити адресу'
            tasks_with_addresses.append(task)
        context['tasks'] = tasks_with_addresses
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, 'Дана сторінка недоступна.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


@staff_member_required(login_url='signin')
def create_passport(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.status or task.user.passport:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')

    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365)
    passport = Passport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
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
            return redirect('tasks_list')
        else:
            messages.error(request, form.errors)
    form = PassportForm(instance=passport)
    return render(request, 'administration/task_form.html',
                  {'form': form, 'user': task.user, 'task': task, 'title': 'Оформлення паспорту'})


@staff_member_required(login_url='signin')
def create_fpassport(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.status or task.user.foreign_passport:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')
    
    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365)
    passport = ForeignPassport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=task.user.passport.authority
    )
    if request.method == 'POST':
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
    return render(request, 'administration/task_form.html',
                  {'form': form, 'user': task.user, 'task': task, 'title': 'Оформлення закордонного паспорту'})


@staff_member_required(login_url='signin')
def restore_passport(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.status:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')
    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365+2)
    new_passport = Passport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=task.user.passport.authority
    )
    if request.method == 'POST':
        form = PassportForm(request.POST, request.FILES, instance=new_passport)
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
    form = PassportForm(instance=new_passport)
    return render(request, 'administration/task_form.html',
                  {'form': form, 'user': task.user, 'title': 'Поновлення паспорту',  
                   'task': task, 'form_title': 'Встановіть необхідні дані для внутрішнього паспотру:'})


@staff_member_required(login_url='signin')
def restore_fpassport(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.status:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')
    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365+2)
    new_passport = ForeignPassport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=task.user.foreign_passport.authority
    )
    if request.method == 'POST':
        form = ForeignPassportForm(request.POST, request.FILES, instance=new_passport)
        if form.is_valid():
            visas = Visa.objects.filter(foreign_passport=task.user.foreign_passport)
            visas.delete()
            task.user.foreign_passport.delete()

            fp = form.save()
            task.user.foreign_passport = fp
            task.user.save()

            task.status = 1
            task.save()
            messages.success(request, 'Успішно поновлено закордонний паспорт!')
            return redirect('tasks_list')
        else:
            messages.error(request, form.errors)
    form = ForeignPassportForm(instance=new_passport)
    return render(request, 'administration/task_form.html',
                  {'form': form, 'user': task.user,'title': 'Відновлення закордонного паспорту', 
                   'task': task, 'form_title': 'Встановіть необхідні дані для відновлення закордонного паспотру користувача:'})


@staff_member_required(login_url='signin')
def change_address(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.status:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')
    addr = get_object_or_404(Address, pk=task.user_data["address_id"])
    if request.method == 'POST':
        task.user.address = addr
        task.user.save()
        task.status = 1
        task.save()
        messages.success(request, 'Успішно поновлено адресу прописки!')
        return redirect('tasks_list')

    return render(request, 'administration/address_form.html', 
                  {'user': task.user, 'address': addr, 'title': 'Оновлення адреси прописки'})


@staff_member_required(login_url='signin')
def change_name_passport(request, task):
    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365+2)
    new_passport = Passport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=task.user.passport.authority
    )
    if request.method == 'POST':
        passport_form = PassportForm(request.POST, instance=new_passport)
        if passport_form.is_valid():
            task.user.passport.delete()
            task.user.name = task.user_data['name']
            p = passport_form.save()
            task.user.passport = p
            task.user.save()
            task.status = 1
            task.save()
            messages.success(request, 'Успішно поновлено внутрішній паспорт!')
            return redirect('tasks_list')
        else:
            messages.error(request, passport_form.errors)
    passport_form = PassportForm(instance=new_passport)
    return render(request, 'administration/change_name_form.html', 
                  {'user': task.user, 'task': task, 
                   'passport_form': passport_form, 'title': 'Переоформлення імені користувача у документах'})   


@staff_member_required(login_url='signin')
def change_name_all_passports(request, task):
    today = datetime.date.today()
    ten_years_more = today + datetime.timedelta(days=10*365+2)
    new_passport = Passport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=task.user.passport.authority
    )
    new_fpassport = ForeignPassport(date_of_issue=today, 
                        number=randint(10000000, 99999999),
                        date_of_expiry=ten_years_more, 
                        photo=task.user_data['photo'],
                        authority=task.user.foreign_passport.authority
    )
    if request.method == 'POST':
        passport_form = PassportForm(request.POST, instance=new_passport)
        fpassport_form = ForeignPassportForm(request.POST, instance=new_fpassport)
        if passport_form.is_valid() and fpassport_form.is_valid():
            task.user.passport.delete()
            task.user.name = task.user_data['name']
            p = passport_form.save()
            task.user.passport = p

            visas = Visa.objects.filter(foreign_passport=task.user.foreign_passport)
            visas.delete()

            task.user.foreign_passport.delete()
            fp = fpassport_form.save()
            task.user.foreign_passport = fp            
            task.user.save()

            task.status = 1
            task.save()
            messages.success(request, 'Успішно поновлено внутрішній паспорт!')
            return redirect('tasks_list')
        else:
            messages.error(request, passport_form.errors)
            messages.error(request, fpassport_form.errors)
    passport_form = PassportForm(instance=new_passport)
    fpassport_form = ForeignPassportForm(instance=new_fpassport)
    return render(request, 'administration/change_name_form.html', 
                  {'user': task.user, 'task': task, 'fpassport_form': fpassport_form,
                   'passport_form': passport_form, 'title': 'Переоформлення імені користувача у документах'})       


@staff_member_required(login_url='signin')
def change_name(request, task_pk):
    task = get_object_or_404(Task, pk=task_pk)
    if task.status:
        messages.error(request, 'Заявка від цього користувача вже опрацьована.')
        return redirect('tasks_list')
    if not task.user.foreign_passport:
        return change_name_passport(request, task)
    return change_name_all_passports(request, task)


@staff_member_required(login_url='signin')
def change_surname(request, task_pk):
    pass


@staff_member_required(login_url='signin')
def change_patronymic(request, task_pk):
    pass
    
