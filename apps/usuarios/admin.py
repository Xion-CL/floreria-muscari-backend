from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Perfil

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'es_cliente', 'is_staff')
    list_filter = ('es_cliente', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {
            'fields': ('documento', 'telefono', 'direccion', 'comuna', 'es_cliente')
        }),
    )

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'newsletter')