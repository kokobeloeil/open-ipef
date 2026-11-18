from django.db.models import Count, Q
from django.shortcuts import render

from accounts.models import User
from faq.models import Question
from ressources.models import Matiere, Ressource


def home(request):
    publiees = Q(ressources__statut=Ressource.Statut.PUBLIEE)
    context = {
        "dernieres": Ressource.objects.visibles_pour(request.user).select_related("matiere", "auteur")[:6],
        "matieres": Matiere.objects.annotate(nb=Count("ressources", filter=publiees)),
        "questions": Question.objects.visibles()
        .select_related("theme")
        .annotate(nb_reponses=Count("reponses"))
        .order_by("-epinglee", "-cree_le")[:5],
        "stats": {
            "ressources": Ressource.objects.publiees().count(),
            "questions": Question.objects.visibles().count(),
            "equipe": User.objects.filter(
                role__in=[User.Role.CONTRIBUTEUR, User.Role.MODERATEUR, User.Role.ADMIN]
            ).count(),
        },
    }
    return render(request, "core/home.html", context)


def apropos(request):
    return render(request, "core/apropos.html", {"roles": User.Role.choices})
