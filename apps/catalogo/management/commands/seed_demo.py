"""
Carga datos de demostración: catálogo completo, usuarios de prueba, pedidos y reseñas.

Uso:  python manage.py seed_demo            (idempotente: no duplica datos)
      python manage.py seed_demo --pedidos 60
Variables opcionales: DEMO_PASSWORD (clave de los usuarios demo).
"""
import os
import random
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from apps.catalogo import seed_data
from apps.catalogo.models import Categoria, Ocasion, Producto, Resena
from apps.usuarios.models import Usuario
from apps.ventas.models import DetallePedido, Pedido

COMUNAS = ['Punta Arenas', 'Punta Arenas', 'Punta Arenas', 'Puerto Natales', 'Porvenir']
CLIENTES = [
    ('cliente_ana', 'Ana', 'Soto'), ('cliente_luis', 'Luis', 'Vera'), ('cliente_camila', 'Camila', 'Reyes'),
    ('cliente_diego', 'Diego', 'Mansilla'), ('cliente_paula', 'Paula', 'Oyarzún'),
]


class Command(BaseCommand):
    help = 'Carga catálogo, usuarios demo, pedidos y reseñas de ejemplo (idempotente).'

    def add_arguments(self, parser):
        parser.add_argument('--pedidos', type=int, default=45, help='Cantidad de pedidos de ejemplo.')

    @transaction.atomic
    def handle(self, *args, **opts):
        self._catalogo()
        clientes = self._usuarios()
        if Pedido.objects.exists():
            self.stdout.write('Ya existen pedidos: no se generan pedidos de ejemplo.')
        else:
            self._pedidos(clientes, opts['pedidos'])
        self.stdout.write(self.style.SUCCESS(
            f'Listo: {Categoria.objects.count()} categorías, {Producto.objects.count()} productos, '
            f'{Pedido.objects.count()} pedidos, {Resena.objects.count()} reseñas.'))

    # ------------------------------------------------------------------
    def _catalogo(self):
        cats = {}
        for nombre, icono, desc, orden in seed_data.CATEGORIAS:
            cats[nombre], _ = Categoria.objects.get_or_create(
                nombre=nombre, defaults={'slug': slugify(nombre), 'icono': icono, 'descripcion': desc,
                                         'orden': orden, 'activo': True})
        ocas = {n: Ocasion.objects.get_or_create(nombre=n, defaults={'slug': slugify(n)})[0]
                for n in seed_data.OCASIONES}

        media_dir = Path(settings.MEDIA_ROOT) / 'productos'
        for i, d in enumerate(seed_data.PRODUCTOS):
            stock = 0 if i == 6 else 3 if i % 7 == 0 else 50  # algunos con stock bajo para las alertas
            prod, creado = Producto.objects.get_or_create(
                nombre=d['nombre'],
                defaults={
                    'slug': slugify(d['nombre']), 'categoria': cats[d['cat']], 'descripcion': d['desc'],
                    'descripcion_corta': d['desc'][:80] + '...', 'precio_original': d['precio_orig'],
                    'precio_oferta': d['precio_oferta'], 'badge': d['badge'],
                    'destacado': d['badge'] in ('MAS_VENDIDO', 'POPULAR', 'PREMIUM'),
                    'disponible': True, 'stock': stock,
                })
            for n in d['ocasiones']:
                prod.ocasiones.add(ocas[n])
            # Enlaza la foto guardada en media/productos/ si el producto aún no tiene imagen.
            if not prod.imagen_principal and not prod.imagen_url:
                archivos = sorted(media_dir.glob(f'producto_*_{prod.slug}.*'))
                if archivos:
                    prod.imagen_principal = f'productos/{archivos[0].name}'
                    prod.save(update_fields=['imagen_principal'])

    def _usuarios(self):
        clave = os.environ.get('DEMO_PASSWORD', 'Muscari2026!')
        usuarios = []
        for username, nombre, apellido in CLIENTES + [('demo', 'Usuario', 'Demo')]:
            u, creado = Usuario.objects.get_or_create(
                username=username,
                defaults={'first_name': nombre, 'last_name': apellido, 'email': f'{username}@example.com',
                          'ciudad': 'Punta Arenas', 'es_cliente': True})
            if creado:
                u.set_password(clave)
                u.save()
            usuarios.append(u)
        return usuarios

    def _pedidos(self, clientes, cantidad):
        rnd = random.Random(2026)
        productos = list(Producto.objects.filter(disponible=True))
        if not productos:
            return
        estados = ['ENTREGADO'] * 6 + ['EN_CAMINO', 'PREPARANDO', 'CONFIRMADO', 'PENDIENTE', 'CANCELADO']
        pagos = ['TRANSFERENCIA', 'TARJETA', 'WEBPAY', 'WEBPAY', 'EFECTIVO']
        ahora = timezone.now()
        for _ in range(cantidad):
            cliente = rnd.choice(clientes)
            items = rnd.sample(productos, rnd.randint(1, 3))
            lineas = [(p, rnd.randint(1, 2)) for p in items]
            subtotal = sum((p.precio_final * c for p, c in lineas), Decimal('0'))
            envio = Decimal('0') if subtotal >= settings.ENVIO_GRATIS_DESDE else Decimal(settings.COSTO_ENVIO)
            fecha = ahora - timedelta(days=rnd.randint(0, 150), hours=rnd.randint(0, 23))
            estado = rnd.choice(estados)
            pedido = Pedido.objects.create(
                usuario=cliente, nombre_cliente=cliente.nombre_completo, email=cliente.email,
                telefono='+56 9 5555 0000', direccion_entrega=f'Calle {rnd.randint(100, 999)}',
                comuna=rnd.choice(COMUNAS), subtotal=subtotal, costo_envio=envio, total=subtotal + envio,
                metodo_pago=rnd.choice(pagos), estado=estado, pago_realizado=(estado == 'ENTREGADO'),
                fecha_entrega_deseada=fecha.date() + timedelta(days=1))
            for p, c in lineas:
                DetallePedido.objects.create(pedido=pedido, producto=p, cantidad=c, precio_unitario=p.precio_final)
            Pedido.objects.filter(pk=pedido.pk).update(fecha_creacion=fecha)

        comentarios = ['Excelente calidad, llegó a tiempo.', 'Muy lindo regalo, a ella le encantó.',
                       'Buena atención y flores frescas.', 'Todo perfecto, lo recomiendo.']
        for p in rnd.sample(productos, min(8, len(productos))):
            u = rnd.choice(clientes)
            Resena.objects.get_or_create(producto=p, usuario=u, defaults={
                'nombre_cliente': u.first_name, 'valoracion': rnd.randint(4, 5),
                'comentario': rnd.choice(comentarios), 'aprobado': True})
        for p in Producto.objects.filter(resenas__isnull=False).distinct():
            rs = p.resenas.filter(aprobado=True)
            p.resenas_count = rs.count()
            p.promedio_resenas = round(Decimal(sum(r.valoracion for r in rs)) / p.resenas_count, 2)
            p.save(update_fields=['resenas_count', 'promedio_resenas'])
