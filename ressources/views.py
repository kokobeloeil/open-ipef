from django.conf import settings
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, F, Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import equipe_requise, moderateur_requis

from .forms import ModerationForm, RessourceForm
from .models import Matiere, Ressource


def liste(request):
    base = Ressource.objects.visibles_pour(request.user)
    qs = base.select_related("matiere", "auteur")

    matiere_active = None
    if slug := request.GET.get("matiere"):
        matiere_active = Matiere.objects.filter(slug=slug).first()
        if matiere_active:
            qs = qs.filter(matiere=matiere_active)

    type_actif = request.GET.get("type", "")
    if type_actif in Ressource.Type.values:
        qs = qs.filter(type=type_actif)
    else:
        type_actif = ""

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(resume__icontains=q) | Q(contenu__icontains=q))

    tri = request.GET.get("tri", "recentes")
    if tri == "populaires":
        qs = qs.order_by("-nb_telechargements", "-publie_le")
    elif tri == "alpha":
        qs = qs.order_by("titre")

    compteurs = dict(base.order_by().values_list("matiere").annotate(n=Count("id")))
    matieres = list(Matiere.objects.all())
    for m in matieres:
        m.nb = compteurs.get(m.pk, 0)

    page = Paginator(qs, 12).get_page(request.GET.get("page"))
    return render(
        request,
        "ressources/liste.html",
        {
            "page": page,
            "matieres": matieres,
            "matiere_active": matiere_active,
            "types": Ressource.Type.choices,
            "type_actif": type_actif,
            "q": q,
            "tri": tri,
            "total": base.count(),
        },
    )


def detail(request, slug):
    r = get_object_or_404(Ressource.objects.select_related("matiere", "auteur", "valide_par"), slug=slug)
    if not r.est_visible_pour(request.user):
        if r.statut != Ressource.Statut.PUBLIEE:
            raise Http404
        if not request.user.is_authenticated:
            messages.info(request, "Connectez-vous pour accéder à cette ressource.")
            return redirect_to_login(request.get_full_path())
        # Connecté mais niveau insuffisant : on explique plutôt qu'un 404
        return render(request, "ressources/acces_restreint.html", {"r": r}, status=403)
    similaires = (
        Ressource.objects.visibles_pour(request.user)
        .filter(matiere=r.matiere)
        .exclude(pk=r.pk)
        .select_related("matiere")[:4]
    )
    return render(
        request,
        "ressources/detail.html",
        {"r": r, "similaires": similaires, "peut_modifier": r.peut_modifier(request.user)},
    )


def telecharger(request, slug):
    r = get_object_or_404(Ressource, slug=slug)
    if not r.fichier or not r.est_visible_pour(request.user):
        raise Http404
    if not request.GET.get("apercu"):
        Ressource.objects.filter(pk=r.pk).update(nb_telechargements=F("nb_telechargements") + 1)
    if settings.USE_S3:
        return redirect(r.fichier.url)  # URL signée, valable quelques minutes
    try:
        return FileResponse(r.fichier.open("rb"), filename=r.nom_fichier)
    except FileNotFoundError:
        raise Http404


def _enregistrer(request, form, ressource_existante=None):
    r = form.save(commit=False)
    action = request.POST.get("action", "soumettre")
    if ressource_existante is None:
        r.auteur = request.user
    deja_publiee = ressource_existante is not None and ressource_existante.statut == Ressource.Statut.PUBLIEE

    if action == "brouillon" and not deja_publiee:
        r.statut = Ressource.Statut.BROUILLON
        msg = "Brouillon enregistré."
    elif deja_publiee:
        msg = "Modifications enregistrées."
    elif request.user.est_moderateur:
        r.statut = Ressource.Statut.PUBLIEE
        r.publie_le = timezone.now()
        r.valide_par = request.user
        msg = "Ressource publiée."
    else:
        r.statut = Ressource.Statut.EN_ATTENTE
        r.motif_refus = ""
        msg = "Ressource envoyée : elle sera visible dès qu'un·e modérateur·rice l'aura validée."
    r.save()
    messages.success(request, msg)
    return r


@equipe_requise
def creer(request):
    form = RessourceForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        r = _enregistrer(request, form)
        return redirect(r)
    return render(request, "ressources/form.html", {"form": form, "creation": True})


@equipe_requise
def modifier(request, slug):
    r = get_object_or_404(Ressource, slug=slug)
    if not r.peut_modifier(request.user):
        raise PermissionDenied
    ancien = Ressource.objects.get(pk=r.pk)
    form = RessourceForm(request.POST or None, request.FILES or None, instance=r)
    if request.method == "POST" and form.is_valid():
        r = _enregistrer(request, form, ressource_existante=ancien)
        return redirect(r)
    return render(request, "ressources/form.html", {"form": form, "creation": False, "r": r})


@equipe_requise
def supprimer(request, slug):
    r = get_object_or_404(Ressource, slug=slug)
    if not r.peut_modifier(request.user):
        raise PermissionDenied
    if request.method == "POST":
        if r.fichier:
            r.fichier.delete(save=False)
        r.delete()
        messages.success(request, "Ressource supprimée.")
        return redirect("ressources:mes_ressources")
    return render(request, "ressources/supprimer.html", {"r": r})


@equipe_requise
def mes_ressources(request):
    qs = request.user.ressources.select_related("matiere").order_by("-modifie_le")
    statut = request.GET.get("statut", "")
    if statut in Ressource.Statut.values:
        qs = qs.filter(statut=statut)
    return render(
        request,
        "ressources/mes_ressources.html",
        {"ressources": qs, "statuts": Ressource.Statut.choices, "statut_actif": statut},
    )


@moderateur_requis
def moderation(request):
    en_attente = (
        Ressource.objects.filter(statut=Ressource.Statut.EN_ATTENTE)
        .select_related("matiere", "auteur")
        .order_by("cree_le")
    )
    return render(request, "ressources/moderation.html", {"ressources": en_attente})


@moderateur_requis
@require_POST
def moderer(request, slug):
    r = get_object_or_404(Ressource, slug=slug)
    form = ModerationForm(request.POST)
    if form.is_valid():
        if form.cleaned_data["decision"] == "valider":
            r.statut = Ressource.Statut.PUBLIEE
            r.publie_le = r.publie_le or timezone.now()
            r.valide_par = request.user
            r.motif_refus = ""
            messages.success(request, f"« {r.titre} » est publiée.")
        else:
            r.statut = Ressource.Statut.REFUSEE
            r.motif_refus = form.cleaned_data["motif"]
            messages.info(request, f"« {r.titre} » a été renvoyée à son auteur·rice.")
        r.save()
    return redirect(request.POST.get("next") or "ressources:moderation")
