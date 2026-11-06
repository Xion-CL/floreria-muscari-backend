# 🌸 La Cabaña de Muscari — Backend (Django + Supabase)

Evaluación 2 de **Backend**, integrada con el proyecto **Proyecto Integrado** (florería *La Cabaña de Muscari*, Punta Arenas).
Aplicación web en **Django 6** con base de datos **PostgreSQL en Supabase**, lista para desplegar gratis en **Render**.

## Qué incluye (según la rúbrica)

| Criterio | Dónde está |
|---|---|
| **CRUD y modelos Django ORM** | Productos y categorías (`/catalogo/panel/…`), movimientos de inventario, pedidos. Modelos con validaciones, `ProtectedError` controlado, slugs automáticos. |
| **Autenticación y sesiones** | Registro, login (usuario o correo), logout, perfil (`apps/usuarios`). Rutas del panel protegidas con `LoginRequiredMixin`; menú y vistas cambian según la sesión; "vistos recientemente" guardado en sesión. |
| **Reportabilidad** | `/reportes/` — dashboard con `Count`, `Sum`, `Avg`, `TruncMonth`, `annotate`, gráficos (Chart.js) y exportación CSV. |
| **Despliegue en la nube** | `render.yaml`, `build.sh`, WhiteNoise, gunicorn, `DEBUG=False`, variables de entorno. Ver `INSTRUCCIONES_DESPLIEGUE.txt`. |
| **Costos y uso de IA** | `/reportes/costos/` (se calcula desde `apps/reportes/costos.py`) y `COSTOS_Y_GUION_PRESENTACION.txt`. |
| **Presentación / demo** | Guion paso a paso en `COSTOS_Y_GUION_PRESENTACION.txt`. |

Relación con *Proyecto Integrado*: catálogo por categorías y ocasiones, carrito, pedidos con entrega, inventario con alerta de stock bajo, reseñas, contacto por WhatsApp y API REST (`/api/…`) para el frontend en GitHub Pages.

## Arranque rápido (local)

```bash
python -m venv venv
venv\Scripts\activate            # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # Linux/Mac: cp .env.example .env   -> editar valores
python manage.py migrate
python manage.py seed_demo       # catálogo + usuarios demo + pedidos de ejemplo
python manage.py createsuperuser # opcional (acceso a /admin/)
python manage.py runserver
```

Sin `DATABASE_URL` usa SQLite local; con la URL de Supabase usa la base en la nube.
Usuarios demo (creados por `seed_demo`): `demo` / `Muscari2026!` (o la clave de `DEMO_PASSWORD`).

## Estructura

```
config/            settings (por entorno), urls, wsgi
apps/core/         inicio, health check, mixins de acceso, utilidades
apps/usuarios/     usuario personalizado, registro/login/perfil, validación de RUT
apps/catalogo/     categorías, ocasiones, productos, reseñas, CRUD, API REST, seed_demo
apps/ventas/       pedidos, checkout, gestión de estados (devuelve stock al cancelar)
apps/inventario/   movimientos de stock y alertas
apps/reportes/     dashboard, exportación CSV, costos del proyecto
templates/ static/ media/   interfaz, estilos/JS, fotos del catálogo
```

## Pruebas

```bash
python manage.py test      # 24 pruebas (catálogo, filtros, auth, CRUD, checkout, reportes)
```

## Seguridad

* No hay contraseñas ni claves en el código: todo va en variables de entorno (`.env` está en `.gitignore`).
* El precio y el stock del pedido se calculan **en el servidor**, nunca desde el navegador.
* `DEBUG=False`, cookies seguras y CSRF activos en producción.

Equipo: Pinto · Ovalle · Tihuel — Proyecto Integrado / Ingeniería de Software.
