from django.urls import path

from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.InventarioView.as_view(), name='inventario'),
    path('movimientos/', views.MovimientoListView.as_view(), name='movimientos'),
    path('movimientos/nuevo/', views.MovimientoCreateView.as_view(), name='movimiento_crear'),
]
