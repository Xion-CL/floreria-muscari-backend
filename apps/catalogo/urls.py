from django.urls import path

from . import views

app_name = 'catalogo'

urlpatterns = [
    # Público
    path('', views.ProductoListView.as_view(), name='lista'),
    path('categoria/<slug:categoria_slug>/', views.ProductoListView.as_view(), name='categoria-productos'),
    path('ocasion/<slug:ocasion_slug>/', views.ProductoListView.as_view(), name='ocasion-productos'),
    path('producto/<slug:slug>/', views.ProductoDetailView.as_view(), name='detalle'),
    path('producto/<slug:slug>/resena/', views.ResenaCreateView.as_view(), name='resena'),

    # Panel de gestión (requiere sesión)
    path('panel/productos/', views.ProductoPanelListView.as_view(), name='panel_productos'),
    path('panel/productos/nuevo/', views.ProductoCreateView.as_view(), name='producto_crear'),
    path('panel/productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto_editar'),
    path('panel/productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto_eliminar'),
    path('panel/categorias/', views.CategoriaPanelListView.as_view(), name='panel_categorias'),
    path('panel/categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_crear'),
    path('panel/categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('panel/categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_eliminar'),
]
