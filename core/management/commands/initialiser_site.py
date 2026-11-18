from django.core.management.base import BaseCommand

from faq.models import Theme
from ressources.models import Matiere

# Liste indicative : à adapter aux épreuves réelles du concours depuis l'admin.
MATIERES = [
    ("Mathématiques", "📐", "#2f5d46"),
    ("Physique", "🔭", "#2f6f8f"),
    ("Chimie", "⚗️", "#8a5a9e"),
    ("Biologie & écologie", "🌿", "#5f8f3b"),
    ("Sciences de la Terre", "🏔️", "#8c6a43"),
    ("Économie & politiques publiques", "📊", "#b8693a"),
    ("Culture générale", "📚", "#a0453f"),
    ("Anglais", "🇬🇧", "#3d5a99"),
    ("Oral & entretien", "🎤", "#c0892b"),
    ("Méthodologie", "🧭", "#55606e"),
]

THEMES = [
    ("Inscription & calendrier", "Dossier, dates, conditions d'accès"),
    ("Épreuves écrites", "Programme, format, attentes du jury"),
    ("Épreuves orales", "Entretien, préparation, conseils"),
    ("Révisions & organisation", "Planning, ressources, méthode"),
    ("Formation & carrière IPEF", "Scolarité, postes, métiers"),
    ("Autre", ""),
]


class Command(BaseCommand):
    help = "Crée les matières et thèmes de FAQ par défaut (sans écraser l'existant)."

    def handle(self, *args, **options):
        for i, (nom, icone, couleur) in enumerate(MATIERES):
            _, cree = Matiere.objects.get_or_create(
                nom=nom, defaults={"icone": icone, "couleur": couleur, "ordre": i}
            )
            if cree:
                self.stdout.write(f"  + matière {nom}")
        for i, (nom, desc) in enumerate(THEMES):
            _, cree = Theme.objects.get_or_create(nom=nom, defaults={"description": desc, "ordre": i})
            if cree:
                self.stdout.write(f"  + thème {nom}")
        self.stdout.write(self.style.SUCCESS("Initialisation terminée."))
