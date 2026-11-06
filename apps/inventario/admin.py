from django.contrib import admin
from .models import Proveedor, MovimientoStock

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'contacto', 'telefono', 'activo')
    search_fields = ('nombre', 'rut')

@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'fecha')
    list_filter = ('tipo',)
    readonly_fields = ('stock_anterior', 'stock_nuevo', 'fecha')