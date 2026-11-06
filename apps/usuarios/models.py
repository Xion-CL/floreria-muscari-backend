from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class Usuario(AbstractUser):
    """
    Usuario personalizado que extiende el modelo por defecto de Django.
    Incluye datos adicionales como RUT, teléfono y dirección.
    """
    TIPO_DOCUMENTO_CHOICES = [
        ('RUT', 'RUT'),
        ('PASAPORTE', 'Pasaporte'),
    ]
    
    tipo_documento = models.CharField(
        max_length=10, 
        choices=TIPO_DOCUMENTO_CHOICES, 
        default='RUT'
    )
    documento = models.CharField(
        max_length=12, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[RegexValidator(regex=r'^[0-9]{7,8}[-]?[0-9Kk]?$', message='RUT inválido')]
    )
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.CharField(max_length=200, blank=True)
    comuna = models.CharField(max_length=100, blank=True)
    ciudad = models.CharField(max_length=100, default='Punta Arenas')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Campo para saber si es cliente o staff
    es_cliente = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"
    
    @property
    def nombre_completo(self):
        return f"{self.first_name} {self.last_name}".strip()


class Perfil(models.Model):
    """
    Perfil extendido del usuario (separado para mantener limpio el modelo).
    Guarda preferencias y datos de facturación.
    """
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE, 
        related_name='perfil'
    )
    foto = models.ImageField(upload_to='perfiles/', null=True, blank=True)
    newsletter = models.BooleanField(default=False)
    notas_internas = models.TextField(blank=True, help_text='Notas internas del equipo')
    
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
    
    def __str__(self):
        return f"Perfil de {self.usuario.username}"