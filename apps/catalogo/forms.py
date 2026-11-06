from django import forms

from .models import Categoria, Producto, Resena


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre', 'categoria', 'ocasiones', 'descripcion_corta', 'descripcion',
            'precio_original', 'precio_oferta', 'stock', 'stock_minimo',
            'imagen_principal', 'imagen_url', 'badge', 'destacado', 'disponible', 'envio_gratis',
        ]
        widgets = {
            'ocasiones': forms.CheckboxSelectMultiple,
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_nombre(self):
        nombre = ' '.join(self.cleaned_data['nombre'].split())
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        duplicado = Producto.objects.filter(nombre__iexact=nombre).exclude(pk=self.instance.pk)
        if duplicado.exists():
            raise forms.ValidationError('Ya existe un producto con ese nombre.')
        return nombre

    def clean_precio_original(self):
        precio = self.cleaned_data['precio_original']
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'icono', 'orden', 'activo']

    def clean_nombre(self):
        nombre = ' '.join(self.cleaned_data['nombre'].split())
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['valoracion', 'comentario']
        widgets = {'comentario': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Cuéntanos tu experiencia...'})}
