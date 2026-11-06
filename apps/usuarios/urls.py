from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.IngresarView.as_view(), name='login'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('logout/', views.SalirView.as_view(), name='logout'),
    path('cuenta/perfil/', views.PerfilView.as_view(), name='perfil'),
]
