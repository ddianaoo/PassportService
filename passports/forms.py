from django import forms
from .models import Address, Passport, ForeignPassport


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = '__all__'
        widgets = {
            'country_code': forms.Select(attrs={'class': 'form-control'}),
            'region': forms.TextInput(attrs={'class': 'form-control'}),
            'settlement': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'apartments': forms.TextInput(attrs={'class': 'form-control'}),
            'post_code': forms.NumberInput(attrs={'class': 'form-control'})
        }


class PhotoForm(forms.Form):
    photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control-file'}))


class PassportForm(forms.ModelForm):

    class Meta:
        model = Passport
        fields = ('number', 'authority', 'date_of_issue', 'date_of_expiry')
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'authority': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_of_issue': forms.DateInput(attrs={'class': 'form-control'}),
            'date_of_expiry': forms.DateInput(attrs={'class': 'form-control'}),
        }


class ForeignPassportForm(forms.ModelForm):

    class Meta:
        model = ForeignPassport
        fields = ('number', 'authority', 'date_of_issue', 'date_of_expiry')
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'authority': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_of_issue': forms.DateInput(attrs={'class': 'form-control'}),
            'date_of_expiry': forms.DateInput(attrs={'class': 'form-control'}),
        }
    