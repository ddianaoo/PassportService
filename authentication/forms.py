from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import CustomUser


class UserRegisterForm(UserCreationForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Re-enter password',
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('name', 'surname', 'patronymic', 'email', 'password1', 'password2', 'sex', 'date_of_birth', 'place_of_birth', 'nationality')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),

            'sex': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-control'}),
            'nationality': forms.Select(attrs={'class': 'form-control'}),
        }


class UserLoginForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('email', 'password',)
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise ValidationError('Невірний email або пароль.')
        return self.cleaned_data


class UpdateUserNameForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('name', )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name == self.instance.name:
            raise ValidationError('The new name must be different from the current one.')
        return name


class UpdateUserSurnameForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('surname',)
        widgets = {
            'surname': forms.TextInput(attrs={'class': 'form-control', }),
        }

    def clean_surname(self):
        surname = self.cleaned_data.get('surname')
        if surname == self.instance.surname:
            raise ValidationError('The new surname must be different from the current one.')
        return surname


class UpdateUserPatronymicForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('patronymic', )
        widgets = {
            'patronymic': forms.TextInput(attrs={'class': 'form-control', }),
        }

    def clean_patronymic(self):
        patronymic = self.cleaned_data.get('patronymic')
        if patronymic == self.instance.patronymic:
            raise ValidationError('The new patronymic must be different from the current one.')
        return patronymic
