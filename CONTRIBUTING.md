# Contribuer au développement

Merci de participer ! Quelques règles simples pour travailler à plusieurs sans se marcher dessus.

## Première installation

```bash
git clone https://github.com/<organisation>/prepa-ipef.git
cd prepa-ipef
python -m venv .venv
# Windows : .venv\Scripts\Activate.ps1   —   macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py initialiser_site
python manage.py createsuperuser
python manage.py runserver
```

## Façon de travailler

1. **Ne travaillez jamais directement sur `main`.** Partez toujours d'une branche à jour :
   ```bash
   git switch main
   git pull
   git switch -c ma-fonctionnalite      # ex. faq-notifications, fix-upload-pdf
   ```
2. Faites des commits courts avec un message clair : `git commit -m "FAQ : ajoute le tri par thème"`.
3. Poussez la branche (`git push -u origin ma-fonctionnalite`) et ouvrez une **Pull Request** sur GitHub.
4. Une autre personne relit et valide la PR avant la fusion dans `main`.
5. Les vérifications automatiques (onglet *Actions*) doivent être au vert.

## Modèles et migrations

Si vous modifiez un fichier `models.py` :
```bash
python manage.py makemigrations
python manage.py migrate
```
puis **commitez les fichiers de migration générés** avec votre code. Si deux personnes ont créé des migrations en parallèle, `python manage.py makemigrations --merge` résout le conflit.

## Ce qu'il ne faut jamais publier

Le fichier `.env` (mots de passe, clés), la base `db.sqlite3` et le dossier `media/` sont exclus par `.gitignore`. Ne les ajoutez pas de force. Si un secret a été poussé par erreur, prévenez l'équipe : il faut le changer, pas seulement le supprimer du dépôt.

## Où toucher quoi

| Je veux modifier… | Fichiers |
|---|---|
| Le design | `static/css/style.css`, `templates/` |
| Les ressources | `ressources/` (modèles, vues, formulaires) |
| La FAQ | `faq/` |
| Les comptes et rôles | `accounts/` |
| L'accueil et la page À propos | `core/`, `templates/core/` |
