from django.contrib import admin

from .models import Dendrometro


@admin.register(Dendrometro)
class DendrometroAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "ubicacion",
        "channel_id",
        "activo",
        "ultima_sincronizacion",
    )
    search_fields = ("nombre", "ubicacion")
    list_filter = ("activo",)
    exclude = ("read_api_key",)
    readonly_fields = (
        "nombre",
        "ubicacion",
        "descripcion",
        "activo",
        "channel_id",
        "field_id",
        "state_field_id",
        "configuracion",
        "revision",
        "sincronizado_desde",
        "ultima_sincronizacion",
        "ultimo_error",
        "creado",
        "actualizado",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
