from django.contrib import admin
from .models import Categoria, Ocasion, Producto, ImagenProducto, Resena

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'icono', 'orden', 'activo')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Ocasion)
class OcasionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'activo')
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_original', 'precio_oferta', 'stock', 'badge', 'destacado', 'disponible')
    list_filter = ('categoria', 'badge', 'destacado', 'disponible')
    search_fields = ('nombre', 'descripcion')
    filter_horizontal = ('ocasiones',)
    prepopulated_fields = {'slug': ('nombre',)}
    filter_horizontal = ('ocasiones',)

@admin.register(ImagenProducto)
class ImagenProductoAdmin(admin.ModelAdmin):
    list_display = ('producto', 'orden')

@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'nombre_cliente', 'valoracion', 'aprobado', 'fecha_creacion')
    list_filter = ('valoracion', 'aprobado')