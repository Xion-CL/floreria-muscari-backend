from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class EmailOrUsernameBackend(ModelBackend):
    """Permite iniciar sesión con el nombre de usuario o con el correo electrónico."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        Usuario = get_user_model()
        if username is None:
            username = kwargs.get(Usuario.USERNAME_FIELD)
        if not username or password is None:
            return None
        candidatos = Usuario.objects.filter(
            Q(username__iexact=username) | Q(email__iexact=username)
        ).order_by('id')[:5]
        for user in candidatos:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        return None
