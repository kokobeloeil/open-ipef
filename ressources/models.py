import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


def slug_unique(instance, valeur, champ="slug", longueur=200):
    base = slugify(valeur)[:longueur] or "element"
    slug, i = base, 2
    modele = type(instance)
    while modele.objects.filter(**{champ: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base}-{i}"
        i += 1
    return slug


def valider_taille(fichier):
    limite = settings.MAX_UPLOAD_MB * 1024 * 1024
    if fichier.size > limite:
        raise ValidationError(f"Le fichier dépasse la taille maximale de {settings.MAX_UPLOAD_MB} Mo.")


class Matiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    icone = models.CharField("icône", max_length=8, blank=True, help_text="Un émoji, par ex. 📐")
    couleur = models.CharField(
        max_length=7, default="#2f5d46", help_text="Couleur hexadécimale, par ex. #2f5d46"
    )
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "matière"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unique(self, self.nom, longueur=100)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{reverse('ressources:liste')}?matiere={self.slug}"


class RessourceQuerySet(models.QuerySet):
    def publiees(self):
        return self.filter(statut=Ressource.Statut.PUBLIEE)

    def visibles_pour(self, user):
        return self.publiees().filter(visibilite__in=Ressource.visibilites_pour(user))


class Ressource(models.Model):
    class Type(models.TextChoices):
        COURS = "cours", "Cours"
        FICHE = "fiche", "Fiche de synthèse"
        EXERCICES = "exercices", "Exercices"
        ANNALE = "annale", "Annale"
        CORRIGE = "corrige", "Corrigé"
        METHODO = "methodo", "Méthodologie"
        ORAL = "oral", "Préparation à l'oral"
        LIEN = "lien", "Lien utile"

    class Visibilite(models.TextChoices):
        PUBLIC = "public", "Public"
        INSCRITS = "inscrits", "Utilisateurs connectés"
        ADMISSIBLES = "admissibles", "Admissibles"
        EQUIPE = "equipe", "Membres de la promo IPEF"

    class Statut(models.TextChoices):
        BROUILLON = "brouillon", "Brouillon"
        EN_ATTENTE = "en_attente", "En attente de validation"
        PUBLIEE = "publiee", "Publiée"
        REFUSEE = "refusee", "Refusée"

    titre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    matiere = models.ForeignKey(Matiere, on_delete=models.PROTECT, related_name="ressources", verbose_name="matière")
    type = models.CharField(max_length=20, choices=Type.choices, default=Type.COURS)
    resume = models.CharField("résumé", max_length=300, help_text="Une ou deux phrases affichées dans les listes.")
    contenu = models.TextField(
        blank=True,
        help_text="Facultatif. Markdown accepté ; formules LaTeX entre $…$ ou $$…$$.",
    )
    fichier = models.FileField(
        upload_to="ressources/%Y/%m/",
        blank=True,
        validators=[FileExtensionValidator(settings.EXTENSIONS_AUTORISEES), valider_taille],
        help_text=f"PDF, documents bureautiques, images, archives… ({settings.MAX_UPLOAD_MB} Mo max.)",
    )
    lien = models.URLField("lien externe", blank=True)
    annee = models.PositiveSmallIntegerField("année", null=True, blank=True, help_text="Pour les annales.")
    visibilite = models.CharField("visibilité", max_length=20, choices=Visibilite.choices, default=Visibilite.PUBLIC)
    statut = models.CharField(max_length=20, choices=Statut.choices, default=Statut.EN_ATTENTE)
    motif_refus = models.CharField("motif du refus", max_length=300, blank=True)

    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="ressources"
    )
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="+"
    )
    nb_telechargements = models.PositiveIntegerField("téléchargements", default=0)
    cree_le = models.DateTimeField("créée le", auto_now_add=True)
    modifie_le = models.DateTimeField("modifiée le", auto_now=True)
    publie_le = models.DateTimeField("publiée le", null=True, blank=True)

    objects = RessourceQuerySet.as_manager()

    class Meta:
        ordering = ["-publie_le", "-cree_le"]
        indexes = [models.Index(fields=["statut", "visibilite"])]

    def __str__(self):
        return self.titre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slug_unique(self, self.titre)
        super().save(*args, **kwargs)

    def clean(self):
        if not (self.fichier or self.lien or self.contenu.strip()):
            raise ValidationError("Ajoutez au moins un fichier, un lien ou un contenu rédigé.")

    def get_absolute_url(self):
        return reverse("ressources:detail", args=[self.slug])

    # -- Fichier ----------------------------------------------------------
    @property
    def nom_fichier(self):
        return os.path.basename(self.fichier.name) if self.fichier else ""

    @property
    def extension(self):
        return os.path.splitext(self.fichier.name)[1].lstrip(".").lower() if self.fichier else ""

    @property
    def est_pdf(self):
        return self.extension == "pdf"

    @property
    def taille(self):
        try:
            return self.fichier.size if self.fichier else 0
        except (OSError, ValueError):
            return 0

    # -- Droits -----------------------------------------------------------
    @classmethod
    def visibilites_pour(cls, user):
        """Niveaux de visibilité accessibles à cet utilisateur (du plus ouvert au plus restreint)."""
        V = cls.Visibilite
        if not user.is_authenticated:
            return [V.PUBLIC]
        if user.est_equipe:
            return [V.PUBLIC, V.INSCRITS, V.ADMISSIBLES, V.EQUIPE]
        if user.est_admissible:
            return [V.PUBLIC, V.INSCRITS, V.ADMISSIBLES]
        return [V.PUBLIC, V.INSCRITS]

    def est_visible_pour(self, user):
        if self.statut != self.Statut.PUBLIEE:
            return user.is_authenticated and (user == self.auteur or user.est_moderateur)
        return self.visibilite in self.visibilites_pour(user)

    def peut_modifier(self, user):
        return user.is_authenticated and (
            user.est_moderateur or (user.est_equipe and user == self.auteur)
        )
