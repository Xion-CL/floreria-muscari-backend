from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView

from apps.core.mixins import PanelAccessMixin, usuario_puede_gestionar

from .forms import CheckoutForm
from .models import Pedido
from .services import StockInsuficiente, cambiar_estado, crear_pedido


class CheckoutView(LoginRequiredMixin, View):
    """Finalizar compra: exige sesión iniciada. El carrito vive en el navegador (localStorage)."""
    template_name = 'ventas/checkout.html'

    def get(self, request):
        u = request.user
        form = CheckoutForm(initial={
            'nombre_cliente': u.nombre_completo or u.username, 'email': u.email, 'telefono': u.telefono,
            'direccion_entrega': u.direccion, 'comuna': u.comuna, 'ciudad': u.ciudad,
        })
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                pedido = crear_pedido(usuario=request.user, form=form)
            except StockInsuficiente as exc:
                messages.error(request, str(exc))
                return render(request, self.template_name, {'form': form})
            messages.success(request, f'¡Pedido #{pedido.pk} creado con éxito!')
            return redirect(f"{reverse('ventas:pedido_detalle', args=[pedido.pk])}?nuevo=1")
        return render(request, self.template_name, {'form': form})


class MisPedidosView(LoginRequiredMixin, ListView):
    template_name = 'ventas/mis_pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).annotate(n_items=Count('detalles'))


class PedidoDetalleView(LoginRequiredMixin, DetailView):
    template_name = 'ventas/pedido_detalle.html'
    context_object_name = 'pedido'

    def get_queryset(self):
        return Pedido.objects.prefetch_related('detalles__producto')

    def get_object(self, queryset=None):
        pedido = super().get_object(queryset)
        if pedido.usuario_id != self.request.user.pk and not usuario_puede_gestionar(self.request.user):
            raise PermissionDenied
        return pedido

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['es_nuevo'] = self.request.GET.get('nuevo') == '1'
        ctx['estados'] = Pedido.ESTADO_CHOICES
        ctx['puede_gestionar'] = usuario_puede_gestionar(self.request.user)
        return ctx


class PedidoPanelListView(PanelAccessMixin, ListView):
    template_name = 'ventas/panel_pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 12

    def get_queryset(self):
        g = self.request.GET
        qs = Pedido.objects.select_related('usuario').annotate(n_items=Count('detalles'))
        if g.get('estado'):
            qs = qs.filter(estado=g['estado'])
        if g.get('q'):
            q = g['q']
            qs = qs.filter(Q(nombre_cliente__icontains=q) | Q(email__icontains=q) | Q(telefono__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx.update({'estados': Pedido.ESTADO_CHOICES, 'estado_sel': self.request.GET.get('estado', ''),
                    'q': self.request.GET.get('q', ''), 'querystring': params.urlencode()})
        return ctx


class PedidoEstadoView(PanelAccessMixin, View):
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk)
        nuevo = request.POST.get('estado')
        if nuevo not in dict(Pedido.ESTADO_CHOICES):
            messages.error(request, 'Estado inválido.')
        else:
            cambiar_estado(pedido, nuevo, request.user)
            messages.success(request, f'Pedido #{pedido.pk} actualizado a "{dict(Pedido.ESTADO_CHOICES)[nuevo]}".')
        destino = request.POST.get('next', '')
        if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}):
            return redirect(destino)
        return redirect('ventas:panel_pedidos')
