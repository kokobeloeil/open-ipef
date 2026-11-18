from django.contrib import admin

from .models import Question, Reponse, Theme


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ("nom", "ordre")
    list_editable = ("ordre",)
    prepopulated_fields = {"slug": ("nom",)}


class ReponseInline(admin.StackedInline):
    model = Reponse
    extra = 0
    raw_id_fields = ("auteur",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("titre", "theme", "auteur", "epinglee", "resolue", "masquee", "cree_le")
    list_filter = ("epinglee", "resolue", "masquee", "theme")
    list_editable = ("epinglee", "resolue", "masquee")
    search_fields = ("titre", "contenu")
    raw_id_fields = ("auteur",)
    filter_horizontal = ("soutiens",)
    inlines = [ReponseInline]
