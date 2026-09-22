from django import template
from core.mixins import usuario_tiene_cargo

register = template.Library()


@register.simple_tag
def puede_configurar_dendrometros(user):
    return usuario_tiene_cargo(user)
