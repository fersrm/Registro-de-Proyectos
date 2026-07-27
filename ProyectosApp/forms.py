from django import forms
from django.utils import timezone
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from .models import Proyecto, IntegranteProyecto, RecursoProyecto
from django.core.exceptions import ValidationError
import os


def validar_imagen(imagen):

    if not imagen:
        return

    formatos_validos = [".jpg", ".jpeg", ".png", ".webp"]

    extension = os.path.splitext(imagen.name)[1].lower()

    if extension not in formatos_validos:
        raise ValidationError("Formato no permitido. Use JPG, PNG o WEBP.")

    limite_mb = 5

    if imagen.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"La imagen no puede superar {limite_mb} MB.")


def validar_recurso_archivo(archivo):

    if not archivo:
        return

    formatos_validos = [".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".webm"]

    extension = os.path.splitext(archivo.name)[1].lower()

    if extension not in formatos_validos:
        raise ValidationError(
            "Formato no permitido. Use imágenes JPG, PNG, WEBP o videos MP4, MOV, WEBM."
        )

    limite_mb = 30

    if archivo.size > limite_mb * 1024 * 1024:
        raise ValidationError(f"El recurso no puede superar {limite_mb} MB.")


class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            "titulo",
            "fecha_inicio",
            "empresa_organizacion",
            "lugar",
            "descripcion",
            "objetivos",
            "trl",
            "docente_lider",
            "imagen_1",
            "imagen_2",
            "imagen_3",
        ]

        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "descripcion": forms.Textarea(
                attrs={
                    "rows": 8,
                    "maxlength": 1200,
                    "placeholder": "Ingrese una descripción detallada del proyecto...",
                }
            ),
            "objetivos": forms.Textarea(
                attrs={
                    "rows": 6,
                    "maxlength": 300,
                    "placeholder": "Ingrese los objetivos del proyecto...",
                }
            ),
        }

        labels = {
            "titulo": "Título del proyecto",
            "fecha_inicio": "Fecha de inicio",
            "empresa_organizacion": "Empresa u organización asociada",
            "lugar": "Lugar",
            "descripcion": "Descripción del proyecto",
            "objetivos": "Objetivos del proyecto",
            "trl": "Grado de madurez tecnológica (TRL)",
            "docente_lider": "Docente líder",
            "imagen_1": "Imagen 1",
            "imagen_2": "Imagen 2",
            "imagen_3": "Imagen 3",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["docente_lider"].queryset = User.objects.filter(is_active=True)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_enctype = "multipart/form-data"
        self.helper.add_input(Submit("submit", "Guardar proyecto"))

    def clean_fecha_inicio(self):
        fecha = self.cleaned_data.get("fecha_inicio")

        if fecha and fecha > timezone.localdate():
            raise forms.ValidationError(
                "La fecha de inicio no puede ser mayor a la fecha actual."
            )

        return fecha

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion", "").strip()

        if len(descripcion) < 100:
            raise forms.ValidationError(
                "La descripción debe tener al menos 100 caracteres."
            )

        if len(descripcion) > 1200:
            raise forms.ValidationError(
                "La descripción no puede superar los 1200 caracteres."
            )

        return descripcion

    def clean_objetivos(self):
        objetivos = self.cleaned_data.get("objetivos", "").strip()

        if len(objetivos) < 50:
            raise forms.ValidationError(
                "Los objetivos deben tener al menos 50 caracteres."
            )

        if len(objetivos) > 300:
            raise forms.ValidationError(
                "Los objetivos no pueden superar los 300 caracteres."
            )

        return objetivos

    def clean_imagen_1(self):
        imagen = self.cleaned_data.get("imagen_1")
        validar_imagen(imagen)
        return imagen

    def clean_imagen_2(self):
        imagen = self.cleaned_data.get("imagen_2")
        validar_imagen(imagen)
        return imagen

    def clean_imagen_3(self):
        imagen = self.cleaned_data.get("imagen_3")
        validar_imagen(imagen)
        return imagen


class IntegranteProyectoForm(forms.ModelForm):
    class Meta:
        model = IntegranteProyecto
        fields = ["nombre", "rol"]

        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Nombre del integrante"}),
        }


IntegranteProyectoFormSet = inlineformset_factory(
    Proyecto, IntegranteProyecto, form=IntegranteProyectoForm, extra=1, can_delete=True
)


class RecursoProyectoForm(forms.ModelForm):
    class Meta:
        model = RecursoProyecto
        fields = [
            "titulo",
            "archivo",
            "url",
            "descripcion",
        ]

        widgets = {
            "descripcion": forms.TextInput(
                attrs={"placeholder": "Breve descripción del recurso"}
            ),
            "url": forms.URLInput(attrs={"placeholder": "https://..."}),
        }

    def clean_archivo(self):
        archivo = self.cleaned_data.get("archivo")
        validar_recurso_archivo(archivo)
        return archivo

    def clean(self):
        cleaned_data = super().clean()

        archivo = cleaned_data.get("archivo")
        url = cleaned_data.get("url")

        if not archivo and not url:
            raise ValidationError(
                "Debe ingresar un recurso válido: archivo, enlace o ambos."
            )

        return cleaned_data


RecursoProyectoFormSet = inlineformset_factory(
    Proyecto, RecursoProyecto, form=RecursoProyectoForm, extra=1, can_delete=True
)
