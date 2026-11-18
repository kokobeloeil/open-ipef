from django.urls import path

from . import views

app_name = "ressources"

urlpatterns = [
    path("", views.liste, name="liste"),
    path("ajouter/", views.creer, name="creer"),
    path("mes-ressources/", views.mes_ressources, name="mes_ressources"),
    path("moderation/", views.moderation, name="moderation"),
    path("r/<slug:slug>/", views.detail, name="detail"),
    path("r/<slug:slug>/fichier/", views.telecharger, name="telecharger"),
    path("r/<slug:slug>/modifier/", views.modifier, name="modifier"),
    path("r/<slug:slug>/supprimer/", views.supprimer, name="supprimer"),
    path("r/<slug:slug>/moderer/", views.moderer, name="moderer"),
]
