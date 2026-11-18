import hmac

from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm

from .models import User


class InscriptionForm(UserCreationForm):
    code_equipe = forms.CharField(
        label="Code promotion",
        required=False,
        help_text="Facultatif : réservé aux membres de la promotion IPEF qui alimentent le site.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "promotion")
        labels = {"username": "Nom d'utilisateur"}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cette adresse.")
        return email

    def clean_code_equipe(self):
        code = self.cleaned_data.get("code_equipe", "").strip()
        if code:
            attendu = settings.CODE_EQUIPE
            if not attendu or not hmac.compare_digest(code, attendu):
                raise forms.ValidationError("Code promotion incorrect.")
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get("code_equipe"):
            user.role = User.Role.CONTRIBUTEUR
        if commit:
            user.save()
        return user


class ProfilForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "promotion", "bio")
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Cette adresse est déjà utilisée.")
        return email
