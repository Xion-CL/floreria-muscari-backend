from django.contrib import messages
from django.db.models import F
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from apps.catalogo.models import Producto
from apps.core.mixins import PanelAccessMixin

from .forms import MovimientoForm
from .models import MovimientoStock


class InventarioView(PanelAccessMixin, ListView):
    """Estado del stock con alertas de stock bajo / agotado."""
    template_name = 'inventario/inventario.html'
    context_object_name = 'productos'
    paginate_by = 15

    def get_queryset(self):
        qs = Producto.objects.select_related('categoria').order_by('stock', 'nombre')
        estado = self.request.GET.get('estado')
        if estado == 'agotado':
            qs = qs.filter(stock=0)
        elif estado == 'bajo':
            qs = qs.filter(stock__gt=0, stock__lte=F('stock_minimo'))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['estado'] = self.request.GET.get('estado', '')
        ctx['querystring'] = f"estado={ctx['estado']}" if ctx['estado'] in ('bajo', 'agotado') else ''
        ctx['n_agotados'] = Producto.objects.filter(stock=0).count()
        ctx['n_bajos'] = Producto.objects.filter(stock__gt=0, stock__lte=F('stock_minimo')).count()
        return ctx


class MovimientoListView(PanelAccessMixin, ListView):
    template_name = 'inventario/movimientos.html'
    context_object_name = 'movimientos'
    paginate_by = 20
    queryset = MovimientoStock.objects.select_related('producto', 'usuario')


class MovimientoCreateView(PanelAccessMixin, CreateView):
    form_class = MovimientoForm
    template_name = 'inventario/movimiento_form.html'
    success_url = reverse_lazy('inventario:movimientos')

    def get_initial(self):
        inicial = super().get_initial()
        pk = self.request.GET.get('producto', '')
        if pk.isdigit():
            inicial['producto'] = int(pk)
        return inicial

    def form_valid(self, form):
        mov = form.save(usuario=self.request.user)
        messages.success(self.request, f'Movimiento registrado: {mov.producto.nombre} '
                                       f'({mov.stock_anterior} → {mov.stock_nuevo}).')
        return redirect(self.success_url)
