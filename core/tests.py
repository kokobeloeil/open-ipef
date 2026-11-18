from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from faq.models import Question
from ressources.models import Matiere, Ressource


class PagesPubliquesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.matiere = Matiere.objects.create(nom="Mathématiques")
        cls.contrib = User.objects.create_user("contrib", "c@ex.fr", "mdp-solide-123", role=User.Role.CONTRIBUTEUR)
        cls.publique = Ressource.objects.create(
            titre="Fiche publique", matiere=cls.matiere, resume="r", contenu="Soit $x^2$",
            statut=Ressource.Statut.PUBLIEE, auteur=cls.contrib,
        )
        cls.interne = Ressource.objects.create(
            titre="Note interne", matiere=cls.matiere, resume="r", contenu="x",
            statut=Ressource.Statut.PUBLIEE, visibilite=Ressource.Visibilite.EQUIPE, auteur=cls.contrib,
        )
        Question.objects.create(titre="Comment s'inscrire ?", contenu="?")

    def test_pages_principales(self):
        for nom in ("core:home", "core:apropos", "ressources:liste", "faq:liste", "accounts:login", "accounts:inscription"):
            with self.subTest(nom=nom):
                self.assertEqual(self.client.get(reverse(nom)).status_code, 200)

    def test_detail_ressource_publique(self):
        r = self.client.get(self.publique.get_absolute_url())
        self.assertContains(r, "Fiche publique")

    def test_ressource_interne_invisible_aux_anonymes(self):
        r = self.client.get(self.interne.get_absolute_url())
        self.assertEqual(r.status_code, 302)  # renvoyé vers la connexion

    def test_ressource_interne_visible_equipe(self):
        self.client.force_login(self.contrib)
        self.assertEqual(self.client.get(self.interne.get_absolute_url()).status_code, 200)

    def test_niveaux_de_visibilite(self):
        reservee = Ressource.objects.create(
            titre="Conseils oral", matiere=self.matiere, resume="r", contenu="x",
            statut=Ressource.Statut.PUBLIEE, visibilite=Ressource.Visibilite.ADMISSIBLES, auteur=self.contrib,
        )
        candidat = User.objects.create_user("cand2", "c2@ex.fr", "mdp-solide-123")
        admissible = User.objects.create_user("adm", "a@ex.fr", "mdp-solide-123", role=User.Role.ADMISSIBLE)

        # Candidat·e : ni admissibles ni promo
        self.client.force_login(candidat)
        self.assertEqual(self.client.get(reservee.get_absolute_url()).status_code, 403)
        self.assertEqual(self.client.get(self.interne.get_absolute_url()).status_code, 403)

        # Admissible : ressources admissibles, mais pas les documents internes
        self.client.force_login(admissible)
        self.assertEqual(self.client.get(reservee.get_absolute_url()).status_code, 200)
        self.assertEqual(self.client.get(self.interne.get_absolute_url()).status_code, 403)
        self.assertEqual(self.client.get(reverse("ressources:creer")).status_code, 403)

        # Membre de la promo : tout
        self.client.force_login(self.contrib)
        self.assertEqual(self.client.get(reservee.get_absolute_url()).status_code, 200)

        visibles = set(Ressource.objects.visibles_pour(admissible).values_list("titre", flat=True))
        self.assertEqual(visibles, {"Fiche publique", "Conseils oral"})

    def test_candidat_ne_peut_pas_deposer(self):
        candidat = User.objects.create_user("cand", "x@ex.fr", "mdp-solide-123")
        self.client.force_login(candidat)
        self.assertEqual(self.client.get(reverse("ressources:creer")).status_code, 403)
