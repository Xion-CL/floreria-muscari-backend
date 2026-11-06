from decimal import Decimal
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Case, Count, DecimalField, F, Q, When
from django.db.models.deletion import ProtectedError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.core.mixins import PanelAccessMixin

from .forms import CategoriaForm, ProductoForm, ResenaForm
from .models import Categoria, Ocasion, Producto, Resena

ORDENES = {
    'destacados': ('-destacado', '-fecha_creacion'),
    'nuevos': ('-fecha_creacion',),
    'precio_asc': ('precio_calc', 'nombre'),
    'precio_desc': ('-precio_calc', 'nombre'),
    'nombre': ('nombre',),
}


def productos_vistos(request, excluir=None):
    """Productos que el visitante vio recientemente (se guardan en la sesión)."""
    ids = [i for i in request.session.get('vistos', []) if i != excluir]
    if not ids:
        return []
    productos = {p.pk: p for p in Producto.objects.filter(pk__in=ids, disponible=True)}
    return [productos[i] for i in ids if i in productos][:4]


# ---------------------------------------------------------------------------
# Catálogo público
# ---------------------------------------------------------------------------
class ProductoListView(ListView):
    """Catálogo con filtros por categoría, ocasión, texto y orden.

    Se usa en /catalogo/, /catalogo/categoria/<slug>/ y /catalogo/ocasion/<slug>/
    (los enlaces del menú y del footer apuntan a estas URL).
    """
    template_name = 'catalogo/lista.html'
    context_object_name = 'productos'
    paginate_by = 9

    def get_queryset(self):
        req = self.request
        self.categoria = self.ocasion = None

        if self.kwargs.get('categoria_slug'):
            self.categoria = get_object_or_404(Categoria, slug=self.kwargs['categoria_slug'], activo=True)
        elif req.GET.get('categoria'):
            self.categoria = Categoria.objects.filter(slug=req.GET['categoria'], activo=True).first()

        if self.kwargs.get('ocasion_slug'):
            self.ocasion = get_object_or_404(Ocasion, slug=self.kwargs['ocasion_slug'], activo=True)
        elif req.GET.get('ocasion'):
            self.ocasion = Ocasion.objects.filter(slug=req.GET['ocasion'], activo=True).first()

        self.q = req.GET.get('q', '').strip()
        self.orden = req.GET.get('orden', 'destacados')
        if self.orden not in ORDENES:
            self.orden = 'destacados'
        self.solo_oferta = req.GET.get('oferta') == '1'

        qs = Producto.objects.filter(disponible=True).select_related('categoria')
        if self.categoria:
            qs = qs.filter(categoria=self.categoria)
        if self.ocasion:
            qs = qs.filter(ocasiones=self.ocasion)
        if self.q:
            qs = qs.filter(Q(nombre__icontains=self.q) | Q(descripcion__icontains=self.q)
                           | Q(descripcion_corta__icontains=self.q))
        if self.solo_oferta:
            qs = qs.filter(precio_oferta__isnull=False, precio_oferta__lt=F('precio_original'))

        qs = qs.annotate(precio_calc=Case(
            When(precio_oferta__isnull=False, precio_oferta__lt=F('precio_original'), then=F('precio_oferta')),
            default=F('precio_original'),
            output_field=DecimalField(max_digits=10, decimal_places=0),
        ))
        return qs.distinct().order_by(*ORDENES[self.orden])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx.update({
            'categoria': self.categoria,
            'ocasion': self.ocasion,
            'q': self.q,
            'orden': self.orden,
            'solo_oferta': self.solo_oferta,
            'total': ctx['paginator'].count,
            'querystring': params.urlencode(),
            'categorias': Categoria.objects.filter(activo=True),
            'ocasiones': Ocasion.objects.filter(activo=True),
            'ordenes': [('destacados', 'Destacados'), ('nuevos', 'Más nuevos'), ('precio_asc', 'Precio: menor a mayor'),
                        ('precio_desc', 'Precio: mayor a menor'), ('nombre', 'Nombre A-Z')],
            'vistos': productos_vistos(self.request),
        })
        return ctx


class ProductoDetailView(DetailView):
    template_name = 'catalogo/detalle.html'
    context_object_name = 'producto'
    queryset = Producto.objects.filter(disponible=True).select_related('categoria').prefetch_related('ocasiones')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Contexto de sesión: recordar los últimos productos vistos.
        vistos = [i for i in self.request.session.get('vistos', []) if i != obj.pk]
        vistos.insert(0, obj.pk)
        self.request.session['vistos'] = vistos[:8]
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.object
        resenas = p.resenas.filter(aprobado=True).select_related('usuario')
        mensaje = f'Hola! Me interesa el producto "{p.nombre}" (${int(p.precio_final):,}). ¿Está disponible?'.replace(',', '.')
        ctx.update({
            'resenas': resenas[:20],
            'form_resena': ResenaForm(),
            'relacionados': Producto.objects.filter(categoria=p.categoria, disponible=True).exclude(pk=p.pk)[:4],
            'vistos': productos_vistos(self.request, excluir=p.pk),
            'whatsapp_url': f'https://wa.me/{settings.WHATSAPP_NUMBER}?text={quote(mensaje)}',
        })
        return ctx


class ResenaCreateView(LoginRequiredMixin, View):
    def post(self, request, slug):
        producto = get_object_or_404(Producto, slug=slug, disponible=True)
        form = ResenaForm(request.POST)
        if Resena.objects.filter(producto=producto, usuario=request.user).exists():
            messages.warning(request, 'Ya dejaste una reseña para este producto.')
        elif form.is_valid():
            resena = form.save(commit=False)
            resena.producto = producto
            resena.usuario = request.user
            resena.nombre_cliente = request.user.first_name or request.user.username
            resena.aprobado = True
            resena.save()
            agg = producto.resenas.filter(aprobado=True).aggregate(n=Count('id'), prom=Avg('valoracion'))
            producto.resenas_count = agg['n']
            producto.promedio_resenas = round(Decimal(str(agg['prom'] or 0)), 2)
            producto.save(update_fields=['resenas_count', 'promedio_resenas'])
            messages.success(request, '¡Gracias por tu reseña!')
        else:
            messages.error(request, 'No se pudo guardar la reseña: revisa los datos.')
        return redirect('catalogo:detalle', slug=slug)


# ---------------------------------------------------------------------------
# Panel de gestión: CRUD de productos
# ---------------------------------------------------------------------------
class ProductoPanelListView(PanelAccessMixin, ListView):
    template_name = 'catalogo/panel_productos.html'
    context_object_name = 'productos'
    paginate_by = 10

    def get_queryset(self):
        g = self.request.GET
        qs = Producto.objects.select_related('categoria')
        if g.get('q'):
            qs = qs.filter(Q(nombre__icontains=g['q']) | Q(descripcion__icontains=g['q']))
        if g.get('categoria', '').isdigit():
            qs = qs.filter(categoria_id=int(g['categoria']))
        estado = g.get('estado')
        if estado == 'agotado':
            qs = qs.filter(stock=0)
        elif estado == 'bajo':
            qs = qs.filter(stock__lte=F('stock_minimo'))
        elif estado == 'inactivo':
            qs = qs.filter(disponible=False)
        return qs.order_by('categoria__orden', 'nombre')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx.update({'categorias': Categoria.objects.all(), 'querystring': params.urlencode(),
                    'q': self.request.GET.get('q', ''), 'estado': self.request.GET.get('estado', ''),
                    'categoria_sel': self.request.GET.get('categoria', '')})
        return ctx


class ProductoCreateView(PanelAccessMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'catalogo/producto_form.html'
    success_url = reverse_lazy('catalogo:panel_productos')
    extra_context = {'titulo': 'Nuevo producto'}

    def form_valid(self, form):
        messages.success(self.request, f'Producto "{form.instance.nombre}" creado correctamente.')
        return super().form_valid(form)


class ProductoUpdateView(PanelAccessMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'catalogo/producto_form.html'
    success_url = reverse_lazy('catalogo:panel_productos')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nombre}'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Producto "{form.instance.nombre}" actualizado.')
        return super().form_valid(form)


class ProductoDeleteView(PanelAccessMixin, DeleteView):
    model = Producto
    template_name = 'panel/confirmar_eliminar.html'
    success_url = reverse_lazy('catalogo:panel_productos')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'titulo': 'Eliminar producto', 'cancelar_url': self.success_url})
        return ctx

    def form_valid(self, form):
        nombre = self.object.nombre
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, f'No se puede eliminar "{nombre}" porque tiene pedidos asociados. '
                                         'Puedes marcarlo como no disponible.')
            return redirect(self.success_url)
        messages.success(self.request, f'Producto "{nombre}" eliminado.')
        return HttpResponseRedirect(self.success_url)


# ---------------------------------------------------------------------------
# Panel de gestión: CRUD de categorías
# ---------------------------------------------------------------------------
class CategoriaPanelListView(PanelAccessMixin, ListView):
    template_name = 'catalogo/panel_categorias.html'
    context_object_name = 'categorias'

    def get_queryset(self):
        return Categoria.objects.annotate(n_productos=Count('productos')).order_by('orden', 'nombre')


class CategoriaCreateView(PanelAccessMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'catalogo/categoria_form.html'
    success_url = reverse_lazy('catalogo:panel_categorias')
    extra_context = {'titulo': 'Nueva categoría'}

    def form_valid(self, form):
        messages.success(self.request, f'Categoría "{form.instance.nombre}" creada.')
        return super().form_valid(form)


class CategoriaUpdateView(PanelAccessMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'catalogo/categoria_form.html'
    success_url = reverse_lazy('catalogo:panel_categorias')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titulo'] = f'Editar: {self.object.nombre}'
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f'Categoría "{form.instance.nombre}" actualizada.')
        return super().form_valid(form)


class CategoriaDeleteView(PanelAccessMixin, DeleteView):
    model = Categoria
    template_name = 'panel/confirmar_eliminar.html'
    success_url = reverse_lazy('catalogo:panel_categorias')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({'titulo': 'Eliminar categoría', 'cancelar_url': self.success_url})
        return ctx

    def form_valid(self, form):
        nombre = self.object.nombre
        try:
            self.object.delete()
        except ProtectedError:
            messages.error(self.request, f'No se puede eliminar "{nombre}": tiene productos asociados.')
            return redirect(self.success_url)
        messages.success(self.request, f'Categoría "{nombre}" eliminada.')
        return HttpResponseRedirect(self.success_url)
