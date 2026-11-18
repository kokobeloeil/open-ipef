# Mise en ligne sur Alwaysdata

Alwaysdata est un hébergeur français qui fait tourner Django nativement, fournit PostgreSQL et un disque persistant pour les fichiers déposés, avec HTTPS automatique (Let's Encrypt). Les intitulés de l'interface peuvent varier légèrement : en cas de doute, voir la documentation officielle (help.alwaysdata.com).

> **Quelle offre ?** L'offre gratuite (100 Mo, fichiers + base inclus) suffit pour tester, mais sera vite pleine avec des PDF. L'offre payante d'entrée de gamme donne beaucoup plus d'espace. Vérifiez les tarifs du moment sur alwaysdata.com. Une cotisation de promo couvre largement ce montant.

## 1. Préparer le compte

1. Créez un compte sur alwaysdata.com et notez votre **nom de compte** (ici `moncompte`).
2. **Environnement → Python** : choisissez Python 3.12 (ou plus récent).
3. **Bases de données → PostgreSQL** : créez une base (ex. `moncompte_ipef`) et un utilisateur avec mot de passe.
4. **Accès distant → SSH** : activez l'accès SSH avec mot de passe.

## 2. Récupérer le code

```bash
ssh moncompte@ssh-moncompte.alwaysdata.net
git clone https://github.com/<organisation>/prepa-ipef.git
cd prepa-ipef
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Dépôt privé : GitHub demandera un identifiant. Utilisez un **jeton d'accès personnel** (GitHub → Settings → Developer settings → Fine-grained tokens, accès en lecture seule au dépôt) à la place du mot de passe, ou ajoutez une clé SSH de déploiement au dépôt.

## 3. Configurer le fichier `.env` sur le serveur

```bash
nano .env
```

```ini
DJANGO_SECRET_KEY=<générer : python -c "import secrets; print(secrets.token_urlsafe(50))">
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=moncompte.alwaysdata.net
DJANGO_CSRF_TRUSTED_ORIGINS=https://moncompte.alwaysdata.net
DATABASE_URL=postgres://UTILISATEUR:MOTDEPASSE@postgresql-moncompte.alwaysdata.net/moncompte_ipef
IPEF_CODE_EQUIPE=<code secret à donner à la promo>
USE_S3=False
```

Puis :

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py initialiser_site
python manage.py createsuperuser
```

## 4. Déclarer le site

**Web → Sites → Ajouter un site** :

| Champ | Valeur |
|---|---|
| Adresses | `moncompte.alwaysdata.net` (et votre domaine si vous en avez un) |
| Type | **Python WSGI** |
| Chemin de l'application | `/home/moncompte/prepa-ipef/config/wsgi.py` |
| Répertoire de travail | `/home/moncompte/prepa-ipef` |
| Répertoire du virtualenv | `/home/moncompte/prepa-ipef/.venv` |

Les fichiers statiques sont servis par WhiteNoise, rien d'autre à configurer. Ouvrez `https://moncompte.alwaysdata.net` : le site est en ligne.

## 5. Mettre à jour après chaque modification

Quand des changements sont fusionnés dans `main` sur GitHub :

```bash
ssh moncompte@ssh-moncompte.alwaysdata.net
cd prepa-ipef && source .venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

puis **Web → Sites → Redémarrer** sur votre site.

## 6. Sauvegardes

Alwaysdata fait des sauvegardes quotidiennes, mais gardez aussi une copie régulière de votre côté :

```bash
pg_dump "$DATABASE_URL" > sauvegarde-$(date +%F).sql
tar czf media-$(date +%F).tar.gz media/
```

## Nom de domaine (facultatif)

Achetez un domaine (ex. `prepa-ipef.fr`) chez un registraire, faites-le pointer vers Alwaysdata (ou gérez-le directement chez eux), ajoutez-le dans les adresses du site, puis dans `DJANGO_ALLOWED_HOSTS` et `DJANGO_CSRF_TRUSTED_ORIGINS`. Le certificat HTTPS est généré automatiquement.
