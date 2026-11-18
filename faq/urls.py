from django.urls import path

from . import views

app_name = "faq"

urlpatterns = [
    path("", views.liste, name="liste"),
    path("poser/", views.poser, name="poser"),
    path("<int:pk>/", views.question, name="question"),
    path("<int:pk>/soutenir/", views.soutenir, name="soutenir"),
    path("<int:pk>/action/", views.action_question, name="action"),
    path("reponse/<int:pk>/accepter/", views.accepter_reponse, name="accepter"),
    path("reponse/<int:pk>/supprimer/", views.supprimer_reponse, name="supprimer_reponse"),
]
