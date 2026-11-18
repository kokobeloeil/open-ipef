from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_requis(niveau_min):
    """Restreint une vue aux utilisateurs connectés de niveau >= niveau_min."""

    def decorateur(vue):
        @login_required
        @wraps(vue)
        def enveloppe(request, *args, **kwargs):
            if request.user.niveau < niveau_min:
                raise PermissionDenied
            return vue(request, *args, **kwargs)

        return enveloppe

    return decorateur


from .models import NIVEAU_ADMIN, NIVEAU_ADMISSIBLE, NIVEAU_EQUIPE, NIVEAU_MODERATEUR  # noqa: E402

admissible_requis = role_requis(NIVEAU_ADMISSIBLE)
equipe_requise = role_requis(NIVEAU_EQUIPE)
moderateur_requis = role_requis(NIVEAU_MODERATEUR)
admin_requis = role_requis(NIVEAU_ADMIN)
