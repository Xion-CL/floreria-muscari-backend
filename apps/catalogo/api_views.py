from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Categoria, Ocasion, Producto
from .serializers import CategoriaSerializer, OcasionSerializer, ProductoSerializer


class CategoriaListView(generics.ListAPIView):
    """API: lista todas las categorías activas."""
    queryset = Categoria.objects.filter(activo=True).order_by('orden')
    serializer_class = CategoriaSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class OcasionListView(generics.ListAPIView):
    """API: lista todas las ocasiones activas."""
    queryset = Ocasion.objects.filter(activo=True).order_by('nombre')
    serializer_class = OcasionSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class ProductoListView(generics.ListAPIView):
    """API: productos disponibles. Filtros: ?categoria=slug &ocasion=slug &q=texto"""
    serializer_class = ProductoSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Producto.objects.filter(disponible=True).select_related('categoria')
        p = self.request.query_params
        if p.get('categoria'):
            qs = qs.filter(categoria__slug=p['categoria'])
        if p.get('ocasion'):
            qs = qs.filter(ocasiones__slug=p['ocasion'])
        if p.get('q'):
            qs = qs.filter(Q(nombre__icontains=p['q']) | Q(descripcion__icontains=p['q']))
        return qs.distinct().order_by('-destacado', '-fecha_creacion')


class ProductoDestacadoListView(generics.ListAPIView):
    """API: productos destacados."""
    queryset = (Producto.objects.filter(destacado=True, disponible=True)
                .select_related('categoria').order_by('-fecha_creacion'))
    serializer_class = ProductoSerializer
    permission_classes = [AllowAny]


class ProductoDetailView(generics.RetrieveAPIView):
    """API: detalle de un producto por slug."""
    queryset = Producto.objects.filter(disponible=True).select_related('categoria')
    serializer_class = ProductoSerializer
    lookup_field = 'slug'
    permission_classes = [AllowAny]
