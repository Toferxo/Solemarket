from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Listing, ListingImage, Review


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['marca', 'nombre', 'descripcion', 'talla', 'precio', 'condicion', 'despacho', 'ciudad']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'ej: Air Max 90, Yeezy 350 Zebra...'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Estado, colores, si tiene caja...'}),
            'talla': forms.TextInput(attrs={'placeholder': 'ej: 42'}),
            'precio': forms.NumberInput(attrs={'placeholder': 'ej: 85000'}),
        }
        labels = {
            'nombre': 'Modelo',
            'talla': 'Talla (EUR)',
            'precio': 'Precio (CLP)',
            'condicion': 'Condición',
            'despacho': 'Tipo de despacho',
        }


class ListingImageFormSet(forms.BaseInlineFormSet):
    pass


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    ciudad = forms.CharField(max_length=100, initial='Santiago', label='Ciudad')
    contacto = forms.CharField(max_length=100, required=False, label='WhatsApp o Instagram (opcional)')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'username': 'Nombre de usuario / apodo'}

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['estrellas', 'comentario']
        widgets = {
            'estrellas': forms.RadioSelect(choices=[(i, f'{'★' * i}') for i in range(1, 6)]),
            'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Cuéntanos tu experiencia...'}),
        }
        labels = {
            'estrellas': 'Calificación',
            'comentario': 'Comentario',
        }
