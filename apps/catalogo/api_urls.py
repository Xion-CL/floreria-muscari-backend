from django.urls import path

from . import api_views

app_name = 'api'

urlpatterns = [
    path('categorias/', api_views.CategoriaListView.as_view(), name='categorias-list'),
    path('ocasiones/', api_views.OcasionListView.as_view(), name='ocasiones-list'),
    path('productos/', api_views.ProductoListView.as_view(), name='productos-list'),
    path('productos-destacados/', api_views.ProductoDestacadoListView.as_view(), name='productos-destacados'),
    path('productos/<slug:slug>/', api_views.ProductoDetailView.as_view(), name='producto-detalle'),
]
