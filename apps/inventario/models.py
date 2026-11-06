from django.db import models
from django.conf import settings


class MovimientoStock(models.Model):
    """
    Registro de todos los movimientos de inventario (entradas, salidas, ajustes).
    """
    TIPO_CHOICES = [
        ('ENTRADA', '📥 Entrada (compra a proveedor)'),
        ('SALIDA', '📤 Salida (venta)'),
        ('AJUSTE', '🔧 Ajuste manual'),
        ('DEVOLUCION', '↩️ Devolución'),
        ('MERMA', '🗑️ Merma / daño'),
    ]
    
    producto = models.ForeignKey(
        'catalogo.Producto', 
        on_delete=models.CASCADE, 
        related_name='movimientos'
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField(help_text='Positivo para entradas, negativo para salidas')
    stock_anterior = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        blank=True,
        help_text='Quién registró el movimiento'
    )
    motivo = models.TextField(blank=True)
    referencia = models.CharField(
        max_length=100, 
        blank=True, 
        help_text='N° de factura, pedido, etc.'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Movimiento de Stock'
        verbose_name_plural = 'Movimientos de Stock'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad:+d})"


class Proveedor(models.Model):
    """
    Proveedores de flores, peluches, chocolates, etc.
    """
    nombre = models.CharField(max_length=200)
    rut = models.CharField(max_length=12, blank=True)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre