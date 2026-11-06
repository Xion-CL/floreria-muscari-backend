from django.utils.text import slugify


def slug_unico(instancia, valor, max_length=50):
    """Genera un slug único para el modelo de `instancia` a partir de `valor`."""
    base = slugify(valor)[: max_length - 5].strip('-') or 'item'
    modelo = instancia.__class__
    slug, n = base, 2
    while modelo.objects.filter(slug=slug).exclude(pk=instancia.pk).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug
