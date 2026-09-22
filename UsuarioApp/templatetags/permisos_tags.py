from django import template

from core.mixins import (
    usuario_puede_editar_proyecto as puede_editar_proyecto_helper,
)
from core.mixins import (
    usuario_tiene_cargo,
)

register = template.Library()


@register.simple_tag
def puede_administrar(user):
    return usuario_tiene_cargo(user)


@register.simple_tag
def puede_editar_proyecto(user, proyecto):
    return puede_editar_proyecto_helper(user, proyecto)
