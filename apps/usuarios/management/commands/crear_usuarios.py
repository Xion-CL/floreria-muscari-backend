"""
Crea el administrador del sitio (superusuario) leyendo las claves desde variables de entorno.
Nunca se escriben contraseñas en el código.

  ADMIN_USERNAME (por defecto: admin_completo)   ADMIN_EMAIL   ADMIN_PASSWORD (obligatoria)
"""
import os

from django.core.management.base import BaseCommand

from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = 'Crea (si no existe) el usuario administrador a partir de variables de entorno.'

    def handle(self, *args, **opts):
        username = os.environ.get('ADMIN_USERNAME', 'admin_completo')
        email = os.environ.get('ADMIN_EMAIL', 'admin@cabanamuscari.com')
        password = os.environ.get('ADMIN_PASSWORD')
        if not password:
            self.stdout.write('ADMIN_PASSWORD no definida: no se crea el administrador.')
            return
        user, creado = Usuario.objects.get_or_create(
            username=username,
            defaults={'email': email, 'first_name': 'Administrador', 'is_staff': True,
                      'is_superuser': True, 'es_cliente': False})
        if creado:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Administrador "{username}" creado.'))
        else:
            self.stdout.write(f'El usuario "{username}" ya existe.')
