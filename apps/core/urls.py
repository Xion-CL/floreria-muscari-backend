from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('carrito/', TemplateView.as_view(template_name='carrito.html'), name='carrito'),
    path('contacto/', TemplateView.as_view(template_name='contacto.html'), name='contacto'),
    path('combos/', TemplateView.as_view(template_name='combos.html'), name='combos'),
    path('salud/', views.salud, name='salud'),
]
