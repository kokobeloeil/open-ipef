from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"

urlpatterns = [
    path(
        "connexion/",
        auth_views.LoginView.as_view(
            template_name="accounts/connexion.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("deconnexion/", auth_views.LogoutView.as_view(), name="logout"),
    path("inscription/", views.inscription, name="inscription"),
    path("profil/", views.profil, name="profil"),
    path(
        "mot-de-passe/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/mot_de_passe.html",
            success_url=reverse_lazy("accounts:profil"),
        ),
        name="password_change",
    ),
    path("equipe/", views.equipe, name="equipe"),
    path("equipe/<int:pk>/role/", views.changer_role, name="changer_role"),
]
