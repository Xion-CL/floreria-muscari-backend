from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Aplicación web (plantillas Django)
    path('', include('apps.core.urls')),            # inicio, carrito, contacto, combos, /salud/
    path('', include('apps.usuarios.urls')),        # login, registro, logout, perfil
    path('catalogo/', include('apps.catalogo.urls')),
    path('compras/', include('apps.ventas.urls')),
    path('inventario/', include('apps.inventario.urls')),
    path('reportes/', include('apps.reportes.urls')),

    # API REST (la puede consumir el frontend alojado en GitHub Pages)
    path('api/', include('apps.catalogo.api_urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Imágenes del catálogo (carpeta media/ incluida en el repositorio)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

handler404 = 'apps.core.views.error_404'
