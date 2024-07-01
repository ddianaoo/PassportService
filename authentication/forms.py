from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


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
    

class ReadOnlyUserForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ('name', 'surname', 'patronymic', 'sex', 'date_of_birth', 'place_of_birth', 'nationality', 'record_number')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'surname': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'sex': forms.Select(attrs={'class': 'form-control', 'disabled': 'true'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'readonly': 'readonly'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'nationality': forms.Select(attrs={'class': 'form-control', 'disabled': 'true'}),
            'record_number': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }
    