from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Utilisateur du site, avec un rôle qui détermine ses droits.

    Hiérarchie (chaque rôle a les droits des rôles inférieurs) :
      0. Candidat·e         : consulte les ressources, pose des questions, répond.
      1. Admissible         : candidat·e admissible, accède aux ressources de préparation aux oraux.
      2. Contributeur·rice  : membre de la promo IPEF, dépose des ressources (soumises à validation).
      3. Modérateur·rice    : valide les ressources, épingle/masque les questions.
      4. Administrateur·rice : gère les rôles des membres.
    """

    class Role(models.TextChoices):
        CANDIDAT = "candidat", "Candidat·e"
        ADMISSIBLE = "admissible", "Admissible"
        CONTRIBUTEUR = "contributeur", "Contributeur·rice"
        MODERATEUR = "moderateur", "Modérateur·rice"
        ADMIN = "admin", "Administrateur·rice"

    email = models.EmailField("adresse e-mail", unique=True)
    role = models.CharField("rôle", max_length=20, choices=Role.choices, default=Role.CANDIDAT)
    promotion = models.CharField(
        "promotion", max_length=60, blank=True, help_text="Ex. « IPEF 2026 » ou « Candidat 2027 »."
    )
    bio = models.CharField("présentation", max_length=280, blank=True)

    class Meta:
        verbose_name = "utilisateur"
        ordering = ["username"]

    # -- Droits -----------------------------------------------------------
    @property
    def niveau(self):
        if self.is_superuser:
            return NIVEAU_ADMIN
        return ROLE_NIVEAUX.get(self.role, 0)

    @property
    def est_admissible(self):
        """Admissible ou membre de la promo (les membres voient tout ce que voient les admissibles)."""
        return self.niveau >= NIVEAU_ADMISSIBLE

    @property
    def est_equipe(self):
        """Membre de la promo IPEF (contributeur, modérateur ou administrateur)."""
        return self.niveau >= NIVEAU_EQUIPE

    @property
    def est_moderateur(self):
        return self.niveau >= NIVEAU_MODERATEUR

    @property
    def est_admin(self):
        return self.niveau >= NIVEAU_ADMIN

    # -- Affichage --------------------------------------------------------
    @property
    def classe_badge(self):
        if self.est_equipe:
            return "badge-equipe"
        if self.est_admissible:
            return "badge-admissible"
        return "badge-muted"

    @property
    def nom_affiche(self):
        return self.get_full_name() or self.username

    @property
    def initiales(self):
        if self.first_name or self.last_name:
            return f"{self.first_name[:1]}{self.last_name[:1]}".upper()
        return self.username[:2].upper()


NIVEAU_ADMISSIBLE = 1
NIVEAU_EQUIPE = 2
NIVEAU_MODERATEUR = 3
NIVEAU_ADMIN = 4

ROLE_NIVEAUX = {
    User.Role.CANDIDAT: 0,
    User.Role.ADMISSIBLE: NIVEAU_ADMISSIBLE,
    User.Role.CONTRIBUTEUR: NIVEAU_EQUIPE,
    User.Role.MODERATEUR: NIVEAU_MODERATEUR,
    User.Role.ADMIN: NIVEAU_ADMIN,
}
