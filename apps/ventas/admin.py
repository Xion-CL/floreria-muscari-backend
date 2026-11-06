from django.contrib import admin
from .models import Pedido, DetallePedido

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 1

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre_cliente', 'total', 'estado', 'metodo_pago', 'fecha_creacion')
    list_filter = ('estado', 'metodo_pago')
    search_fields = ('nombre_cliente', 'email', 'telefono')
    inlines = [DetallePedidoInline]

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'producto', 'cantidad', 'precio_unitario', 'subtotal')