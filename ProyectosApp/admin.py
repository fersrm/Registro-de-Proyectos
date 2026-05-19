from django.contrib import admin
from .models import Proyecto


class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("titulo",)


admin.site.register(Proyecto, ProyectoAdmin)
