from django import forms

from .models import Question, Reponse


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("titre", "theme", "contenu")
        widgets = {
            "titre": forms.TextInput(attrs={"placeholder": "Ex. Comment se déroule l'oral d'entretien ?"}),
            "contenu": forms.Textarea(attrs={"rows": 6}),
        }


class ReponseForm(forms.ModelForm):
    class Meta:
        model = Reponse
        fields = ("contenu",)
        labels = {"contenu": "Votre réponse"}
        widgets = {"contenu": forms.Textarea(attrs={"rows": 5, "placeholder": "Partagez votre expérience…"})}
