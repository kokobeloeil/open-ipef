# Prépa IPEF — site de partage de ressources

Site Django pour partager cours, fiches, annales et conseils avec les candidats au concours IPEF, avec une foire aux questions ouverte aux candidats.

## Fonctionnalités

- **Ressources** classées par matière et par type (cours, fiche, exercices, annale, corrigé, méthodologie, oral, lien). Chaque ressource peut contenir un fichier, un lien externe et/ou un contenu rédigé en Markdown avec formules LaTeX (rendu KaTeX). Aperçu intégré des PDF, compteur de téléchargements, recherche, filtres et tri.
- **Quatre niveaux de visibilité** : public, utilisateurs connectés, admissibles, membres de la promo IPEF (documents internes).
- **Circuit de validation** : brouillon → en attente → publiée (ou refusée avec motif).
- **FAQ** : les candidats inscrits posent des questions ; tout le monde peut répondre, les réponses de la promo portent le badge « Équipe ». Bouton « Moi aussi », meilleure réponse, questions épinglées comme « fréquentes », masquage par les modérateurs.
- **Fichiers protégés** : ils ne sont jamais servis directement, la vue de téléchargement vérifie les droits (et génère une URL signée temporaire si le stockage S3 est activé).

## Rôles

| Niveau | Rôle | Ce qu'il peut faire |
|---|---|---|
| 0 | Candidat·e | Consulter (public + connectés), poser des questions, répondre, soutenir |
| 1 | Admissible | + voir les ressources « Admissibles » (préparation des oraux…) |
| 2 | Contributeur·rice (promo IPEF) | + déposer des ressources (soumises à validation), voir les documents « Membres de la promo », répondre avec le badge Équipe |
| 3 | Modérateur·rice | + valider/refuser, publier directement, modifier toute ressource, épingler/masquer des questions |
| 4 | Administrateur·rice | + attribuer les rôles, dont le statut d'admissible (page « Membres & rôles ») |

| Visibilité d'une ressource | Qui la voit |
|---|---|
| Public | Tout le monde, sans compte |
| Utilisateurs connectés | Tout compte connecté |
| Admissibles | Admissibles et membres de la promo |
| Membres de la promo IPEF | Contributeurs, modérateurs, administrateurs |

Le statut d'**admissible** est attribué à la main par un administrateur (après vérification, par ex. sur la liste officielle des admissibles). Les membres de la promo deviennent contributeurs automatiquement s'ils saisissent le **code promotion** (`IPEF_CODE_EQUIPE`) à l'inscription. Un administrateur peut ensuite les promouvoir modérateurs.

## Installation en local

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # puis éditer les valeurs
python manage.py makemigrations accounts ressources faq
python manage.py migrate
python manage.py initialiser_site  # matières et thèmes de FAQ par défaut
python manage.py createsuperuser
python manage.py runserver
```

Ouvrir http://127.0.0.1:8000. L'administration Django est sur `/admin/` (matières, thèmes, couleurs et icônes des matières se gèrent là).

> Les matières créées par `initialiser_site` sont indicatives : adaptez-les aux épreuves réelles du concours depuis l'administration.

## Mise en production

1. Mettre `DJANGO_DEBUG=False`, une vraie `DJANGO_SECRET_KEY`, le nom de domaine dans `DJANGO_ALLOWED_HOSTS` et `DJANGO_CSRF_TRUSTED_ORIGINS` (ex. `https://prepa-ipef.fr`).
2. Utiliser PostgreSQL via `DATABASE_URL`.
3. `python manage.py collectstatic` puis lancer `gunicorn config.wsgi` derrière un proxy HTTPS (Nginx, Caddy ou la plateforme d'hébergement).

### Stockage des fichiers

Deux options :

- **Disque du serveur** (`USE_S3=False`) : le plus simple, suffisant tant que le volume reste modeste. Pensez à sauvegarder le dossier `media/`.
- **Stockage objet compatible S3** (`USE_S3=True`) : recommandé pour un volume qui grandit et pour des sauvegardes simples. Fonctionne avec Scaleway Object Storage, OVHcloud Object Storage, Cloudflare R2, AWS S3… Créez un bucket **privé** et renseignez les variables `S3_*`. Les fichiers sont servis via des URLs signées valables 10 minutes.

Comparez les tarifs actuels des fournisseurs avant de vous engager : ils évoluent, et certains proposent un palier gratuit qui peut suffire au démarrage.

## Personnalisation

- Couleurs et typographie : variables CSS en tête de `static/css/style.css`.
- Motif topographique de l'en-tête : `static/img/topo.svg`.
- Extensions de fichiers acceptées et taille max : `EXTENSIONS_AUTORISEES` dans `config/settings.py` et `IPEF_MAX_UPLOAD_MB`.

## Pistes d'évolution

- Vérification de l'adresse e-mail et réinitialisation du mot de passe (nécessite un SMTP).
- Notifications par e-mail aux modérateurs (nouvelle ressource) et aux auteurs de questions (nouvelle réponse).
- Tags libres sur les ressources, favoris, commentaires.
