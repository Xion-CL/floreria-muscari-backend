import json
from datetime import date, timedelta

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.catalogo.models import Categoria, Ocasion, Producto
from apps.inventario.models import MovimientoStock
from apps.reportes import costos
from apps.usuarios.models import Usuario
from apps.usuarios.validators import validar_rut
from apps.ventas.models import Pedido


def crear_datos():
    ramos = Categoria.objects.create(nombre='Ramos', icono='💐', orden=1)
    peluches = Categoria.objects.create(nombre='Peluches', icono='🧸', orden=2)
    cumple = Ocasion.objects.create(nombre='Cumpleaños', slug='cumpleanos')
    p1 = Producto.objects.create(nombre='Ramo Rojo', categoria=ramos, descripcion='Rosas', descripcion_corta='Rosas',
                                 precio_original=30000, precio_oferta=25000, stock=10, destacado=True)
    p2 = Producto.objects.create(nombre='Osito', categoria=peluches, descripcion='Peluche', descripcion_corta='Peluche',
                                 precio_original=20000, stock=5)
    p1.ocasiones.add(cumple)
    return ramos, peluches, cumple, p1, p2


class CatalogoPublicoTests(TestCase):
    def setUp(self):
        self.ramos, self.peluches, self.cumple, self.p1, self.p2 = crear_datos()

    def test_paginas_publicas(self):
        for name in ['index', 'carrito', 'contacto', 'combos', 'login', 'registro', 'catalogo:lista', 'reportes:costos']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)

    def test_slug_automatico(self):
        self.assertEqual(self.p1.slug, 'ramo-rojo')
        self.assertEqual(self.ramos.slug, 'ramos')

    def test_filtro_categoria_por_url_footer(self):
        r = self.client.get(reverse('catalogo:categoria-productos', args=['ramos']))
        self.assertContains(r, 'Ramo Rojo')
        self.assertNotContains(r, 'Osito</a>')

    def test_filtro_ocasion_por_url_footer(self):
        r = self.client.get(reverse('catalogo:ocasion-productos', args=['cumpleanos']))
        self.assertContains(r, 'Ramo Rojo')
        self.assertNotContains(r, 'Osito</a>')

    def test_footer_y_navbar_enlazan_a_filtros(self):
        r = self.client.get(reverse('index'))
        self.assertContains(r, '/catalogo/categoria/ramos/')
        self.assertContains(r, '/catalogo/ocasion/cumpleanos/')
        self.assertContains(r, 'id="mobileMenuToggle"')

    def test_categoria_inexistente_404(self):
        self.assertEqual(self.client.get('/catalogo/categoria/no-existe/').status_code, 404)

    def test_busqueda_y_orden(self):
        r = self.client.get(reverse('catalogo:lista'), {'q': 'osito', 'orden': 'precio_asc'})
        self.assertContains(r, 'Osito')
        self.assertNotContains(r, 'Ramo Rojo</a>')

    def test_detalle_guarda_vistos_en_sesion(self):
        self.client.get(reverse('catalogo:detalle', args=[self.p1.slug]))
        self.assertEqual(self.client.session['vistos'], [self.p1.pk])

    def test_api_productos_y_destacados(self):
        r = self.client.get('/api/productos-destacados/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()['results'][0]['nombre'], 'Ramo Rojo')
        self.assertEqual(self.client.get('/api/productos/?categoria=ramos').json()['count'], 1)


class AutenticacionTests(TestCase):
    def test_registro_login_logout(self):
        r = self.client.post(reverse('registro'), {
            'username': 'maria', 'first_name': 'María', 'last_name': 'Pérez', 'email': 'maria@example.com',
            'documento': '', 'telefono': '', 'password1': 'Clave-Segura-2026', 'password2': 'Clave-Segura-2026'})
        self.assertRedirects(r, reverse('index'))
        self.assertTrue(Usuario.objects.get(username='maria').es_cliente)
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        # inicio de sesión con correo electrónico
        r = self.client.post(reverse('login'), {'username': 'maria@example.com', 'password': 'Clave-Segura-2026'})
        self.assertEqual(r.status_code, 302)
        self.assertIn('_auth_user_id', self.client.session)

    def test_registro_correo_duplicado(self):
        Usuario.objects.create_user('a', 'dup@example.com', 'x')
        r = self.client.post(reverse('registro'), {
            'username': 'b', 'first_name': 'B', 'last_name': 'B', 'email': 'DUP@example.com',
            'password1': 'Clave-Segura-2026', 'password2': 'Clave-Segura-2026'})
        self.assertContains(r, 'Ya existe una cuenta')

    def test_rut(self):
        self.assertEqual(validar_rut('12.345.678-5'), '12345678-5')
        with self.assertRaises(Exception):
            validar_rut('12.345.678-9')

    def test_rutas_protegidas(self):
        for name in ['catalogo:panel_productos', 'catalogo:panel_categorias', 'ventas:panel_pedidos',
                     'inventario:inventario', 'reportes:dashboard', 'ventas:checkout', 'perfil']:
            r = self.client.get(reverse(name))
            self.assertEqual(r.status_code, 302, name)
            self.assertIn('/login/', r['Location'])

    @override_settings(PANEL_SOLO_STAFF=True)
    def test_panel_solo_staff(self):
        Usuario.objects.create_user('cli', 'c@example.com', 'pw12345678')
        self.client.login(username='cli', password='pw12345678')
        self.assertEqual(self.client.get(reverse('reportes:dashboard')).status_code, 302)


class CrudTests(TestCase):
    def setUp(self):
        self.ramos, self.peluches, self.cumple, self.p1, self.p2 = crear_datos()
        Usuario.objects.create_user('gestor', 'g@example.com', 'pw12345678')
        self.client.login(username='gestor', password='pw12345678')

    def test_crud_producto(self):
        datos = {'nombre': 'Girasoles', 'categoria': self.ramos.pk, 'descripcion_corta': 'x', 'descripcion': 'Girasoles',
                 'precio_original': 20000, 'precio_oferta': 18000, 'stock': 4, 'stock_minimo': 5, 'badge': 'NINGUNO',
                 'disponible': 'on'}
        self.assertRedirects(self.client.post(reverse('catalogo:producto_crear'), datos), reverse('catalogo:panel_productos'))
        p = Producto.objects.get(nombre='Girasoles')
        datos['precio_original'] = 22000
        self.client.post(reverse('catalogo:producto_editar', args=[p.pk]), datos)
        p.refresh_from_db()
        self.assertEqual(p.precio_original, 22000)
        self.assertEqual(self.client.get(reverse('catalogo:panel_productos')).status_code, 200)
        self.client.post(reverse('catalogo:producto_eliminar', args=[p.pk]))
        self.assertFalse(Producto.objects.filter(pk=p.pk).exists())

    def test_oferta_mayor_que_precio_invalida(self):
        datos = {'nombre': 'Malo', 'categoria': self.ramos.pk, 'descripcion_corta': 'x', 'descripcion': 'x',
                 'precio_original': 10000, 'precio_oferta': 12000, 'stock': 1, 'stock_minimo': 1, 'badge': 'NINGUNO'}
        r = self.client.post(reverse('catalogo:producto_crear'), datos)
        self.assertContains(r, 'precio de oferta debe ser menor')
        self.assertFalse(Producto.objects.filter(nombre='Malo').exists())

    def test_crud_categoria_y_proteccion(self):
        self.client.post(reverse('catalogo:categoria_crear'), {'nombre': 'Globos', 'descripcion': '', 'icono': '🎈', 'orden': 9, 'activo': 'on'})
        cat = Categoria.objects.get(nombre='Globos')
        self.client.post(reverse('catalogo:categoria_eliminar', args=[cat.pk]))
        self.assertFalse(Categoria.objects.filter(pk=cat.pk).exists())
        # categoría con productos no se puede eliminar
        self.client.post(reverse('catalogo:categoria_eliminar', args=[self.ramos.pk]))
        self.assertTrue(Categoria.objects.filter(pk=self.ramos.pk).exists())

    def test_movimiento_stock(self):
        self.client.post(reverse('inventario:movimiento_crear'), {'producto': self.p1.pk, 'tipo': 'ENTRADA', 'cantidad': 5, 'motivo': '', 'referencia': ''})
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.stock, 15)
        r = self.client.post(reverse('inventario:movimiento_crear'), {'producto': self.p1.pk, 'tipo': 'SALIDA', 'cantidad': 99, 'motivo': '', 'referencia': ''})
        self.assertContains(r, 'stock actual')
        self.assertEqual(MovimientoStock.objects.count(), 1)


class VentasYReportesTests(TestCase):
    def setUp(self):
        self.ramos, self.peluches, self.cumple, self.p1, self.p2 = crear_datos()
        self.user = Usuario.objects.create_user('cli', 'c@example.com', 'pw12345678', first_name='Cli')
        self.client.login(username='cli', password='pw12345678')

    def _datos(self, items):
        return {'nombre_cliente': 'Cli', 'email': 'c@example.com', 'telefono': '+56 9 1234 5678',
                'direccion_entrega': 'Calle 1', 'comuna': 'Punta Arenas', 'ciudad': 'Punta Arenas',
                'metodo_pago': 'TRANSFERENCIA', 'fecha_entrega_deseada': (date.today() + timedelta(days=1)).isoformat(),
                'items': json.dumps(items)}

    def test_checkout_crea_pedido_y_descuenta_stock(self):
        r = self.client.post(reverse('ventas:checkout'), self._datos([{'id': self.p1.pk, 'quantity': 2}]))
        pedido = Pedido.objects.get()
        self.assertRedirects(r, f"{reverse('ventas:pedido_detalle', args=[pedido.pk])}?nuevo=1")
        self.assertEqual(pedido.subtotal, 50000)          # 2 x 25.000 (precio de oferta tomado del servidor)
        self.assertEqual(pedido.costo_envio, 0)           # envío gratis desde 50.000
        self.p1.refresh_from_db()
        self.assertEqual(self.p1.stock, 8)
        self.assertEqual(MovimientoStock.objects.filter(tipo='SALIDA').count(), 1)

    def test_checkout_sin_stock(self):
        r = self.client.post(reverse('ventas:checkout'), self._datos([{'id': self.p2.pk, 'quantity': 50}]))
        self.assertContains(r, 'No hay stock suficiente')
        self.assertEqual(Pedido.objects.count(), 0)

    def test_cancelar_pedido_devuelve_stock(self):
        self.client.post(reverse('ventas:checkout'), self._datos([{'id': self.p2.pk, 'quantity': 2}]))
        pedido = Pedido.objects.get()
        Usuario.objects.create_user('gest', 'g@example.com', 'pw12345678')
        self.client.login(username='gest', password='pw12345678')
        self.client.post(reverse('ventas:pedido_estado', args=[pedido.pk]), {'estado': 'CANCELADO'})
        self.p2.refresh_from_db()
        self.assertEqual(self.p2.stock, 5)

    def test_pedido_ajeno_solo_visible_para_gestion(self):
        self.client.post(reverse('ventas:checkout'), self._datos([{'id': self.p1.pk, 'quantity': 1}]))
        pedido = Pedido.objects.get()
        self.assertEqual(self.client.get(reverse('ventas:pedido_detalle', args=[pedido.pk])).status_code, 200)

    def test_seed_demo_y_dashboard(self):
        call_command('seed_demo', pedidos=20, stdout=open('/dev/null', 'w'))
        self.assertGreater(Pedido.objects.count(), 10)
        r = self.client.get(reverse('reportes:dashboard'))
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Ingresos por mes')
        self.assertEqual(self.client.get(reverse('reportes:pedidos_csv')).status_code, 200)
        self.assertEqual(self.client.get(reverse('ventas:panel_pedidos')).status_code, 200)
        self.assertEqual(self.client.get(reverse('inventario:inventario')).status_code, 200)

    def test_calculo_costos(self):
        c = costos.calcular()
        self.assertEqual(c['horas_ia'], sum(f['h_ia'] for f in c['filas']))
        self.assertGreater(c['ahorro'], 0)
        self.assertEqual(c['total_con_ia'], c['costo_hh_ia'] + c['infra_usada'] + c['costo_ia'])
