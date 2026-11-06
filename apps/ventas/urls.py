from django.urls import path

from . import views

app_name = 'ventas'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('mis-pedidos/', views.MisPedidosView.as_view(), name='mis_pedidos'),
    path('pedido/<int:pk>/', views.PedidoDetalleView.as_view(), name='pedido_detalle'),
    path('panel/pedidos/', views.PedidoPanelListView.as_view(), name='panel_pedidos'),
    path('panel/pedidos/<int:pk>/estado/', views.PedidoEstadoView.as_view(), name='pedido_estado'),
]
