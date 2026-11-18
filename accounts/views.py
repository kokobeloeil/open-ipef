from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .decorators import admin_requis
from .forms import InscriptionForm, ProfilForm
from .models import User


def inscription(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    form = InscriptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        if user.est_equipe:
            messages.success(request, "Bienvenue dans l'équipe ! Vous pouvez maintenant déposer des ressources.")
        else:
            messages.success(request, "Bienvenue ! Votre compte a bien été créé.")
        return redirect("core:home")
    return render(request, "accounts/inscription.html", {"form": form})


@login_required
def profil(request):
    form = ProfilForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profil mis à jour.")
        return redirect("accounts:profil")
    stats = {
        "ressources": request.user.ressources.count(),
        "questions": request.user.questions.count(),
        "reponses": request.user.reponses.count(),
    }
    return render(request, "accounts/profil.html", {"form": form, "stats": stats})


@admin_requis
def equipe(request):
    q = request.GET.get("q", "").strip()
    role = request.GET.get("role", "")
    users = User.objects.annotate(nb_ressources=Count("ressources")).order_by("-date_joined")
    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(first_name__icontains=q)
            | Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    if role in User.Role.values:
        users = users.filter(role=role)
    page = Paginator(users, 30).get_page(request.GET.get("page"))
    comptes = dict(User.objects.order_by().values_list("role").annotate(n=Count("id")))
    roles_compte = [(val, label, comptes.get(val, 0)) for val, label in User.Role.choices]
    return render(
        request,
        "accounts/equipe.html",
        {"page": page, "q": q, "role_actif": role, "roles": User.Role.choices, "roles_compte": roles_compte},
    )


@admin_requis
@require_POST
def changer_role(request, pk):
    cible = get_object_or_404(User, pk=pk)
    nouveau = request.POST.get("role")
    if nouveau not in User.Role.values:
        messages.error(request, "Rôle inconnu.")
    elif cible == request.user:
        messages.error(request, "Vous ne pouvez pas modifier votre propre rôle.")
    elif cible.is_superuser and not request.user.is_superuser:
        messages.error(request, "Seul un super-utilisateur peut modifier ce compte.")
    else:
        cible.role = nouveau
        cible.save(update_fields=["role"])
        messages.success(request, f"{cible.nom_affiche} est maintenant {cible.get_role_display().lower()}.")
    return redirect(request.POST.get("next") or "accounts:equipe")
