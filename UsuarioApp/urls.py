from django.urls import path
from UsuarioApp import views

urlpatterns = [
    path("usuarios/", views.UserListView.as_view(), name="User"),
    path("usuarios/<int:pk>/desactivar/", views.UserDeactivateView.as_view(), name="UserDeactivate"),
    path("usuarios/<int:pk>/activar/", views.UserActivateView.as_view(), name="UserActivate"),
    path("registro/", views.UserCreateView.as_view(), name="Register"),
    path("perfil/", views.ProfileUpdateView.as_view(), name="Profile"),
]
