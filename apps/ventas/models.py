from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings


class Pedido(models.Model):
    """
    Pedido realizado por un cliente.
    """
    ESTADO_CHOICES = [
        ('PENDIENTE', '⏳ Pendiente'),
        ('CONFIRMADO', '✅ Confirmado'),
        ('PREPARANDO', '🌸 Preparando'),
        ('EN_CAMINO', '🚚 En camino'),
        ('ENTREGADO', '📦 Entregado'),
        ('CANCELADO', '❌ Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('TRANSFERENCIA', 'Transferencia bancaria'),
        ('TARJETA', 'Tarjeta de crédito/débito'),
        ('WEBPAY', 'WebPay'),
        ('EFECTIVO', 'Efectivo contra entrega'),
    ]
    
    # Cliente
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT, 
        related_name='pedidos',
        null=True, blank=True  # Permite pedidos de invitados
    )
    nombre_cliente = models.CharField(max_length=150)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    
    # Dirección de entrega
    direccion_entrega = models.CharField(max_length=250)
    comuna = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100, default='Punta Arenas')
    instrucciones_entrega = models.TextField(blank=True)
    
    # Mensaje del regalo
    mensaje_tarjeta = models.TextField(blank=True, help_text='Mensaje para la tarjeta del regalo')
    destinatario = models.CharField(max_length=150, blank=True)
    
    # Montos
    subtotal = models.DecimalField(max_digits=10, decimal_places=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    costo_envio = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=0)
    
    # Pago
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    pago_realizado = models.BooleanField(default=False)
    
    # Estado
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    
    # Envío
    envio_gratis = models.BooleanField(default=False)
    fecha_entrega_deseada = models.DateField()
    hora_entrega_deseada = models.TimeField(null=True, blank=True)
    
    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente}"
    
    def save(self, *args, **kwargs):
        # Envío gratis sobre $50.000
        if self.subtotal >= 50000:
            self.envio_gratis = True
            self.costo_envio = 0
        super().save(*args, **kwargs)


class DetallePedido(models.Model):
    """
    Líneas individuales de un pedido (productos comprados).
    """
    pedido = models.ForeignKey(
        Pedido, 
        on_delete=models.CASCADE, 
        related_name='detalles'
    )
    producto = models.ForeignKey(
        'catalogo.Producto', 
        on_delete=models.PROTECT
    )
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=0)
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'
    
    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)