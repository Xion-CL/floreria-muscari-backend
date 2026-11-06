from rest_framework import serializers

from .models import Categoria, Ocasion, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'slug', 'icono', 'descripcion']


class OcasionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ocasion
        fields = ['id', 'nombre', 'slug']


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    categoria_slug = serializers.CharField(source='categoria.slug', read_only=True)
    tiene_descuento = serializers.ReadOnlyField()
    porcentaje_descuento = serializers.ReadOnlyField()
    precio_final = serializers.ReadOnlyField()
    # URL relativa (/media/...) o URL externa; '' si el producto no tiene imagen
    imagen_principal = serializers.CharField(source='imagen_src', read_only=True)

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'slug', 'descripcion_corta', 'precio_original',
            'precio_oferta', 'tiene_descuento', 'porcentaje_descuento', 'precio_final',
            'badge', 'destacado', 'disponible', 'stock', 'categoria_nombre', 'categoria_slug',
            'imagen_principal',
        ]
