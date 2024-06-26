from django import forms
from .models import Address


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
    photo = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}))
