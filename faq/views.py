from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count, Exists, OuterRef, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import QuestionForm, ReponseForm
from .models import Question, Reponse, Theme


def _annoter(qs):
    return qs.annotate(
        nb_reponses=Count("reponses", distinct=True),
        nb_soutiens=Count("soutiens", distinct=True),
        a_reponse_equipe=Exists(Reponse.objects.filter(question=OuterRef("pk"), de_l_equipe=True)),
    )


def liste(request):
    qs = _annoter(Question.objects.visibles().select_related("theme", "auteur"))

    theme_actif = None
    if slug := request.GET.get("theme"):
        theme_actif = Theme.objects.filter(slug=slug).first()
        if theme_actif:
            qs = qs.filter(theme=theme_actif)

    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(titre__icontains=q) | Q(contenu__icontains=q) | Q(reponses__contenu__icontains=q)).distinct()

    filtre = request.GET.get("filtre", "")
    if filtre == "frequentes":
        qs = qs.filter(epinglee=True)
    elif filtre == "sans_reponse":
        qs = qs.filter(nb_reponses=0)
    elif filtre == "resolues":
        qs = qs.filter(resolue=True)
    elif filtre == "populaires":
        qs = qs.order_by("-nb_soutiens", "-cree_le")

    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(
        request,
        "faq/liste.html",
        {
            "page": page,
            "themes": Theme.objects.all(),
            "theme_actif": theme_actif,
            "q": q,
            "filtre": filtre,
        },
    )


def question(request, pk):
    question = get_object_or_404(Question.objects.select_related("theme", "auteur"), pk=pk)
    user = request.user
    if question.masquee and not (user.is_authenticated and user.est_moderateur):
        raise Http404

    form = ReponseForm(request.POST or None)
    if request.method == "POST":
        if not user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if form.is_valid():
            rep = form.save(commit=False)
            rep.question = question
            rep.auteur = user
            rep.de_l_equipe = user.est_equipe
            rep.save()
            messages.success(request, "Merci pour votre réponse !")
            return redirect(f"{question.get_absolute_url()}#reponse-{rep.pk}")

    reponses = question.reponses.select_related("auteur")
    peut_accepter = user.is_authenticated and (user == question.auteur or user.est_moderateur)
    return render(
        request,
        "faq/question.html",
        {
            "question": question,
            "reponses": reponses,
            "form": form,
            "nb_soutiens": question.soutiens.count(),
            "deja_soutenu": user.is_authenticated and question.soutiens.filter(pk=user.pk).exists(),
            "peut_accepter": peut_accepter,
            "similaires": Question.objects.visibles()
            .filter(theme=question.theme)
            .exclude(pk=question.pk)[:5]
            if question.theme
            else [],
        },
    )


@login_required
def poser(request):
    form = QuestionForm(request.POST or None, initial={"titre": request.GET.get("titre", "")})
    if request.method == "POST" and form.is_valid():
        q = form.save(commit=False)
        q.auteur = request.user
        q.save()
        messages.success(request, "Question publiée ! L'équipe et la communauté vont pouvoir vous répondre.")
        return redirect(q)
    return render(request, "faq/poser.html", {"form": form})


@login_required
@require_POST
def soutenir(request, pk):
    question = get_object_or_404(Question.objects.visibles(), pk=pk)
    if question.soutiens.filter(pk=request.user.pk).exists():
        question.soutiens.remove(request.user)
    else:
        question.soutiens.add(request.user)
    return redirect(question)


@login_required
@require_POST
def action_question(request, pk):
    question = get_object_or_404(Question, pk=pk)
    user = request.user
    action = request.POST.get("action")
    if action in ("epingler", "masquer") and not user.est_moderateur:
        raise PermissionDenied
    if action == "resoudre" and not (user == question.auteur or user.est_equipe):
        raise PermissionDenied

    if action == "epingler":
        question.epinglee = not question.epinglee
        messages.success(request, "Question ajoutée aux questions fréquentes." if question.epinglee else "Question retirée des questions fréquentes.")
    elif action == "masquer":
        question.masquee = not question.masquee
        messages.info(request, "Question masquée." if question.masquee else "Question de nouveau visible.")
    elif action == "resoudre":
        question.resolue = not question.resolue
    else:
        raise Http404
    question.save()
    if question.masquee:
        return redirect("faq:liste")
    return redirect(question)


@login_required
@require_POST
def accepter_reponse(request, pk):
    rep = get_object_or_404(Reponse.objects.select_related("question"), pk=pk)
    question = rep.question
    if not (request.user == question.auteur or request.user.est_moderateur):
        raise PermissionDenied
    nouvelle_valeur = not rep.acceptee
    question.reponses.update(acceptee=False)
    rep.acceptee = nouvelle_valeur
    rep.save(update_fields=["acceptee"])
    if nouvelle_valeur and not question.resolue:
        question.resolue = True
        question.save(update_fields=["resolue"])
    return redirect(f"{question.get_absolute_url()}#reponse-{rep.pk}")


@login_required
@require_POST
def supprimer_reponse(request, pk):
    rep = get_object_or_404(Reponse.objects.select_related("question"), pk=pk)
    if not (request.user == rep.auteur or request.user.est_moderateur):
        raise PermissionDenied
    question = rep.question
    rep.delete()
    messages.info(request, "Réponse supprimée.")
    return redirect(question)
