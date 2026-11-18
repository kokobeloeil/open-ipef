from django.contrib import admin
from django.utils import timezone

from .models import Matiere, Ressource


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ("nom", "icone", "couleur", "ordre")
    list_editable = ("ordre",)
    prepopulated_fields = {"slug": ("nom",)}


@admin.action(description="Publier les ressources sélectionnées")
def publier(modeladmin, request, queryset):
    queryset.update(statut=Ressource.Statut.PUBLIEE, publie_le=timezone.now(), valide_par=request.user)


@admin.register(Ressource)
class RessourceAdmin(admin.ModelAdmin):
    list_display = ("titre", "matiere", "type", "statut", "visibilite", "auteur", "nb_telechargements", "cree_le")
    list_filter = ("statut", "visibilite", "type", "matiere")
    search_fields = ("titre", "resume", "contenu")
    prepopulated_fields = {"slug": ("titre",)}
    raw_id_fields = ("auteur", "valide_par")
    readonly_fields = ("nb_telechargements", "cree_le", "modifie_le")
    actions = [publier]
