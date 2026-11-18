from django.conf import settings


def site(request):
    ctx = {"SITE_NAME": settings.SITE_NAME}
    user = getattr(request, "user", None)
    if user is not None and user.is_authenticated and user.est_moderateur:
        from ressources.models import Ressource

        ctx["nb_en_attente"] = Ressource.objects.filter(statut=Ressource.Statut.EN_ATTENTE).count()
    return ctx
