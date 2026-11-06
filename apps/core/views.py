from django.http import HttpResponse
from django.shortcuts import render


def salud(request):
    """Health check para el hosting (no consulta la base de datos)."""
    return HttpResponse('ok', content_type='text/plain')


def error_404(request, exception):
    return render(request, '404.html', status=404)
