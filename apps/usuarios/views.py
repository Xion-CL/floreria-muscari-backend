from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import LoginForm, PerfilForm, RegistroForm


class IngresarView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f'¡Bienvenido/a, {form.get_user().first_name or form.get_user().username}!')
        return super().form_valid(form)


class SalirView(LogoutView):
    """Cierra la sesión (solo por POST, como exige Django)."""
    next_page = reverse_lazy('index')


class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'registro.html'
    success_url = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = user = form.save()
        login(self.request, user, backend='apps.usuarios.backends.EmailOrUsernameBackend')
        messages.success(self.request, '¡Cuenta creada con éxito! Ya iniciaste sesión.')
        return redirect(self.get_success_url())


class PerfilView(LoginRequiredMixin, UpdateView):
    form_class = PerfilForm
    template_name = 'usuarios/perfil.html'
    success_url = reverse_lazy('perfil')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Tu perfil se actualizó correctamente.')
        return super().form_valid(form)
