from django import forms
from django.core.exceptions import ValidationError
from passports.models import Passport
from .models import Task


class PassportForm(forms.ModelForm):

    class Meta:
        model = Passport
        fields = '__all__'
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'record_number': forms.TextInput(attrs={'class': 'form-control'}),
            'authority': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_of_issue': forms.DateInput(attrs={'class': 'form-control'}),
            'date_of_expiry': forms.DateInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
