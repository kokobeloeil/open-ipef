from django import forms

from .models import Ressource


class RessourceForm(forms.ModelForm):
    class Meta:
        model = Ressource
        fields = ("titre", "matiere", "type", "resume", "fichier", "lien", "annee", "visibilite", "contenu")
        widgets = {
            "resume": forms.Textarea(attrs={"rows": 2}),
            "contenu": forms.Textarea(attrs={"rows": 14, "class": "mono"}),
            "titre": forms.TextInput(attrs={"placeholder": "Ex. Fiche : séries entières"}),
            "lien": forms.URLInput(attrs={"placeholder": "https://…"}),
        }


class ModerationForm(forms.Form):
    decision = forms.ChoiceField(choices=[("valider", "Valider"), ("refuser", "Refuser")])
    motif = forms.CharField(max_length=300, required=False)
