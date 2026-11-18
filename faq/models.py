from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Theme(models.Model):
    nom = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    description = models.CharField(max_length=200, blank=True)
    ordre = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["ordre", "nom"]
        verbose_name = "thème"

    def __str__(self):
        return self.nom

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)[:90]
        super().save(*args, **kwargs)


class QuestionQuerySet(models.QuerySet):
    def visibles(self):
        return self.filter(masquee=False)


class Question(models.Model):
    titre = models.CharField(max_length=200, help_text="Votre question en une phrase.")
    contenu = models.TextField("précisions", blank=True, help_text="Contexte, détails… (Markdown accepté)")
    theme = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True, blank=True, related_name="questions", verbose_name="thème")
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="questions")
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)
    epinglee = models.BooleanField("question fréquente", default=False, help_text="Affichée en tête de la FAQ.")
    resolue = models.BooleanField("résolue", default=False)
    masquee = models.BooleanField("masquée", default=False)
    soutiens = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="questions_soutenues")

    objects = QuestionQuerySet.as_manager()

    class Meta:
        ordering = ["-epinglee", "-cree_le"]

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("faq:question", args=[self.pk])


class Reponse(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="reponses")
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="reponses")
    contenu = models.TextField("réponse")
    de_l_equipe = models.BooleanField("réponse de l'équipe", default=False)
    acceptee = models.BooleanField("meilleure réponse", default=False)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-acceptee", "-de_l_equipe", "cree_le"]
        verbose_name = "réponse"

    def __str__(self):
        return f"Réponse à « {self.question} »"
