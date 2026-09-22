from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy

from UsuarioApp.models import Profile


def codigo_cargo_usuario(user):
    """Devuelve el código de cargo sin asumir que existe un perfil."""
    if not user.is_authenticated or not user.is_active:
        return None
    if user.is_superuser:
        return "SUPERUSER"
    try:
        perfil = user.profile
    except Profile.DoesNotExist:
        return None
    if not perfil.position_FK:
        return None
    return perfil.position_FK.permission_code


def usuario_tiene_cargo(user, cargos=("ADMIN", "MANAGER")):
    """Una misma regla para las vistas y los enlaces del menú."""
    codigo = codigo_cargo_usuario(user)
    if codigo == "SUPERUSER":
        return True
    return codigo in cargos


def usuario_puede_editar_proyecto(user, proyecto):
    """Aplica la política común para editar un proyecto."""
    if usuario_tiene_cargo(user):
        return True
    return bool(
        codigo_cargo_usuario(user) == "RESTRICTED" and proyecto.creado_por_id == user.pk
    )


class PermitsPositionMixin(LoginRequiredMixin):
    """
    Permite acceso al módulo solo a usuarios activos
    con cargo ADMIN o MANAGER.
    """

    login_url = "account_login"
    redirect_url = reverse_lazy("Home")

    permisos_docente = ("ADMIN", "MANAGER")

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return self.handle_no_permission()

        if not usuario_tiene_cargo(user, self.permisos_docente):
            return redirect(self.redirect_url)

        return super().dispatch(request, *args, **kwargs)
