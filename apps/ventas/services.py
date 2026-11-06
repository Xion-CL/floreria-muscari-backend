from decimal import Decimal

from django.conf import settings
from django.db import transaction

from apps.catalogo.models import Producto
from apps.inventario.models import MovimientoStock

from .models import DetallePedido, Pedido


class StockInsuficiente(Exception):
    pass


@transaction.atomic
def crear_pedido(*, usuario, form):
    """Crea el pedido con sus detalles, descuenta stock y registra los movimientos."""
    items = form.cleaned_data['items']  # {producto_id: cantidad}
    productos = {p.pk: p for p in Producto.objects.select_for_update().filter(pk__in=items.keys(), disponible=True)}

    faltantes = [pid for pid in items if pid not in productos]
    if faltantes:
        raise StockInsuficiente('Algún producto de tu carrito ya no está disponible.')
    for pid, cant in items.items():
        if cant > productos[pid].stock:
            raise StockInsuficiente(f'No hay stock suficiente de "{productos[pid].nombre}" '
                                    f'(disponible: {productos[pid].stock}).')

    subtotal = sum((productos[pid].precio_final * cant for pid, cant in items.items()), Decimal('0'))
    envio_gratis = subtotal >= settings.ENVIO_GRATIS_DESDE
    costo_envio = Decimal('0') if envio_gratis else Decimal(settings.COSTO_ENVIO)

    pedido = form.save(commit=False)
    pedido.usuario = usuario
    pedido.subtotal = subtotal
    pedido.descuento = Decimal('0')
    pedido.costo_envio = costo_envio
    pedido.envio_gratis = envio_gratis
    pedido.total = subtotal + costo_envio
    pedido.save()

    for pid, cant in items.items():
        prod = productos[pid]
        DetallePedido.objects.create(pedido=pedido, producto=prod, cantidad=cant, precio_unitario=prod.precio_final)
        anterior = prod.stock
        prod.stock = anterior - cant
        prod.save(update_fields=['stock', 'fecha_modificacion'])
        MovimientoStock.objects.create(
            producto=prod, tipo='SALIDA', cantidad=-cant, stock_anterior=anterior, stock_nuevo=prod.stock,
            usuario=usuario, motivo='Venta online', referencia=f'Pedido #{pedido.pk}',
        )
    return pedido


@transaction.atomic
def cambiar_estado(pedido, nuevo_estado, usuario):
    """Cambia el estado; si se cancela, devuelve el stock al inventario."""
    pedido = Pedido.objects.select_for_update().get(pk=pedido.pk)
    if pedido.estado == nuevo_estado:
        return pedido
    if nuevo_estado == 'CANCELADO' and pedido.estado != 'CANCELADO':
        for det in pedido.detalles.select_related('producto'):
            prod = Producto.objects.select_for_update().get(pk=det.producto_id)
            anterior = prod.stock
            prod.stock = anterior + det.cantidad
            prod.save(update_fields=['stock', 'fecha_modificacion'])
            MovimientoStock.objects.create(
                producto=prod, tipo='DEVOLUCION', cantidad=det.cantidad, stock_anterior=anterior,
                stock_nuevo=prod.stock, usuario=usuario, motivo='Pedido cancelado',
                referencia=f'Pedido #{pedido.pk}',
            )
    pedido.estado = nuevo_estado
    if nuevo_estado == 'ENTREGADO':
        pedido.pago_realizado = True
    pedido.save()
    return pedido
