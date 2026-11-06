from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.utils import slug_unico


class Categoria(models.Model):
    """
    Categorías principales: Ramos, Arreglos Florales, Peluches, Chocolates, Combos
    """
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='categorias/', null=True, blank=True)
    icono = models.CharField(
        max_length=10,
        blank=True,
        help_text='Emoji o clase de icono (ej: , 🧸)'
    )
    activo = models.BooleanField(default=True)
    orden = models.PositiveIntegerField(default=0, help_text='Orden de aparición')

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unico(self, self.nombre)
        super().save(*args, **kwargs)


class Ocasion(models.Model):
    """
    Ocasiones: Cumpleaños, Aniversario, Día de la Madre, etc.
    """
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='ocasiones/', null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Ocasión'
        verbose_name_plural = 'Ocasiones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Producto principal: flores, peluches, chocolates, etc.
    """
    BADGE_CHOICES = [
        ('NINGUNO', 'Sin badge'),
        ('MAS_VENDIDO', '⭐ Más vendido'),
        ('POPULAR', '🔥 Popular'),
        ('PREMIUM', '💎 Premium'),
        ('NUEVO', '🌸 Nuevo'),
        ('OFERTA', '💝 Oferta'),
        ('COMBO', '💝 Combo'),
    ]

    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    descripcion = models.TextField()
    descripcion_corta = models.CharField(
        max_length=255,
        blank=True,
        help_text='Descripción breve para tarjetas'
    )

    # Relaciones
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='productos'
    )
    ocasiones = models.ManyToManyField(
        Ocasion,
        blank=True,
        related_name='productos'
    )

    # Precios (en CLP)
    precio_original = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)]
    )
    precio_oferta = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )

    # Inventario
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5, help_text='Alerta cuando stock baja de este valor')

    # Imágenes
    imagen_principal = models.ImageField(upload_to='productos/', blank=True)
    imagen_url = models.URLField(
        'URL de imagen', max_length=500, blank=True,
        help_text='Alternativa a subir un archivo: enlace público de la imagen (https://...)'
    )

    # Metadata
    badge = models.CharField(max_length=20, choices=BADGE_CHOICES, default='NINGUNO')
    resenas_count = models.PositiveIntegerField(default=0)
    promedio_resenas = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0
    )

    # Estado
    destacado = models.BooleanField(default=False, help_text='Aparece en "Productos Destacados"')
    disponible = models.BooleanField(default=True)
    envio_gratis = models.BooleanField(default=False)

    # Timestamps
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-destacado', '-fecha_creacion']
        indexes = [
            models.Index(fields=['categoria', 'disponible']),
            # models.Index(fields=['slug']),  # Comentado: unique=True ya crea índice automático
        ]

    def __str__(self):
        return self.nombre

    def clean(self):
        super().clean()
        if (self.precio_oferta is not None and self.precio_original is not None
                and self.precio_oferta >= self.precio_original):
            raise ValidationError({'precio_oferta': 'El precio de oferta debe ser menor al precio original.'})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unico(self, self.nombre)
        super().save(*args, **kwargs)

    @property
    def imagen_src(self):
        """URL de la imagen a mostrar (URL externa o archivo subido); '' si no hay."""
        if self.imagen_url:
            return self.imagen_url
        if self.imagen_principal:
            return self.imagen_principal.url
        return ''

    @property
    def tiene_descuento(self):
        return self.precio_oferta is not None and self.precio_oferta < self.precio_original

    @property
    def porcentaje_descuento(self):
        if self.tiene_descuento:
            return round((1 - self.precio_oferta / self.precio_original) * 100)
        return 0

    @property
    def precio_final(self):
        return self.precio_oferta if self.tiene_descuento else self.precio_original

    @property
    def stock_bajo(self):
        return self.stock <= self.stock_minimo


class ImagenProducto(models.Model):
    """
    Galería de imágenes adicionales del producto.
    """
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes'
    )
    imagen = models.ImageField(upload_to='productos/galeria/')
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Productos'
        ordering = ['orden']

    def __str__(self):
        return f"Imagen de {self.producto.nombre}"


class Resena(models.Model):
    """
    Reseñas de clientes sobre productos.
    """
    VALORACION_CHOICES = [(i, f'{i} estrellas') for i in range(1, 6)]

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='resenas'
    )
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    nombre_cliente = models.CharField(max_length=100, blank=True)
    valoracion = models.PositiveSmallIntegerField(choices=VALORACION_CHOICES)
    comentario = models.TextField(blank=True)
    aprobado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reseña'  # ✅ CORREGIDO: Era 'Producto'
        verbose_name_plural = 'Reseñas'  # ✅ CORREGIDO: Era 'Productos'
        ordering = ['-fecha_creacion']  # ✅ CORREGIDO: Era '-destacado'
        # ✅ ELIMINADO: indexes con campos 'categoria' y 'disponible' que no existen en Resena

    def __str__(self):
        return f"{self.producto.nombre} - {self.valoracion}★"