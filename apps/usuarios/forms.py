import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Usuario
from .validators import validar_rut


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario o correo',
        widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}),
    )


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label='Nombre', max_length=150)
    last_name = forms.CharField(label='Apellido', max_length=150)
    email = forms.EmailField(label='Correo electrónico')
    documento = forms.CharField(label='RUT (opcional)', required=False, max_length=12)
    telefono = forms.CharField(label='Teléfono (opcional)', required=False, max_length=20)

    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'documento', 'telefono')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return email

    def clean_documento(self):
        valor = (self.cleaned_data.get('documento') or '').strip()
        if not valor:
            return None  # el campo es único y admite NULL
        rut = validar_rut(valor)
        if Usuario.objects.filter(documento=rut).exists():
            raise forms.ValidationError('Este RUT ya está registrado.')
        return rut

    def clean_telefono(self):
        tel = (self.cleaned_data.get('telefono') or '').strip()
        if tel and not re.fullmatch(r'[+\d][\d\s-]{6,19}', tel):
            raise forms.ValidationError('Ingresa un teléfono válido, por ejemplo +56 9 1234 5678.')
        return tel

    def save(self, commit=True):
        user = super().save(commit=False)
        user.es_cliente = True
        if commit:
            user.save()
        return user


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'telefono', 'direccion', 'comuna', 'ciudad')
        labels = {'first_name': 'Nombre', 'last_name': 'Apellido', 'email': 'Correo electrónico',
                  'telefono': 'Teléfono', 'direccion': 'Dirección', 'comuna': 'Comuna', 'ciudad': 'Ciudad'}

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Usuario.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ese correo ya está en uso por otra cuenta.')
        return email
