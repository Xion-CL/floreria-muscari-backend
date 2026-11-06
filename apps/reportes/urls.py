from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('pedidos.csv', views.ExportarPedidosCSV.as_view(), name='pedidos_csv'),
    path('costos/', views.CostosView.as_view(), name='costos'),
]
