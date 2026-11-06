from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


def usuario_puede_gestionar(user):
    """Regla única de acceso al panel de gestión (CRUD, inventario, reportes)."""
    if not user.is_authenticated:
        return False
    if settings.PANEL_SOLO_STAFF:
        return user.is_staff
    return True


class PanelAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Exige sesión iniciada (y, opcionalmente, ser staff) para vistas de gestión."""

    def test_func(self):
        return usuario_puede_gestionar(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'No tienes permisos para acceder a esa sección.')
            return redirect('index')
        return super().handle_no_permission()
