from django.conf import settings

from apps.core.mixins import usuario_puede_gestionar


def sitio(request):
    """Variables disponibles en todas las plantillas (navbar y footer dinámicos)."""
    from apps.catalogo.models import Categoria, Ocasion  # import tardío: evita ciclos

    return {
        'NOMBRE_SITIO': 'La Cabaña de Muscari',
        'WHATSAPP_NUMBER': settings.WHATSAPP_NUMBER,
        'menu_categorias': Categoria.objects.filter(activo=True).order_by('orden', 'nombre'),
        'menu_ocasiones': Ocasion.objects.filter(activo=True).order_by('nombre'),
        'puede_gestionar': usuario_puede_gestionar(request.user),
    }
