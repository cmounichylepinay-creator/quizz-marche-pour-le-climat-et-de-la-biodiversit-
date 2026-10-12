# Les Galets du Climat — première version jouable

Application Flask + SQLite : 60 QCM issus de la fiche action, 3 itinéraires (8/16/36 galets), score 5 points par galet validé + 10 par bonne réponse, classement par pourcentage, cinq premiers visibles, export CSV pour l'organisation.

## Lancer sur un ordinateur

```bash
python -m pip install -r requirements.txt
# Choisir des valeurs secrètes avant toute mise en ligne
export SECRET_KEY='une-longue-cle-secrete-aleatoire'
export ADMIN_KEY='un-code-admin-difficile-a-deviner'
python app.py
```

Sous Windows PowerShell, utiliser `$env:SECRET_KEY='...'` et `$env:ADMIN_KEY='...'` à la place des commandes `export`.

Ouvrir `http://127.0.0.1:5000` sur l'ordinateur. Le classement admin est sur `/admin?key=VOTRE_CLE`.

## Mise en ligne et QR codes

Héberger l'application Flask sur un serveur HTTPS avec **stockage persistant** pour le fichier SQLite (ou remplacer SQLite par une base partagée adaptée à la charge). Définir `SECRET_KEY`, `ADMIN_KEY`, `DATABASE_PATH` et lancer avec un serveur WSGI, par exemple `gunicorn app:app`. Une instance gratuite à disque éphémère ne convient pas pour les résultats réels.

Après avoir obtenu l'URL publique HTTPS :

```bash
python generer_qr.py https://votre-domaine.fr
```

Le dossier `qr_codes/` contiendra les 60 PNG et le tableau `correspondance.csv`. Les liens suivent la forme `https://votre-domaine.fr/galet/1` à `/galet/60`.

## IMPORTANT : limites de cette version de démonstration

- La page `/test/galets` expose les questions pour tester le jeu ; **la désactiver** avant l'événement.
- La lecture d'un QR code ne prouve pas à elle seule la possession du galet. Prévoir une **vérification physique à l'arrivée** ; un lien partagé pourrait sinon être utilisé à distance.
- Le concours comporte des galets à usage unique ramassés par les premiers marcheurs : un départ simultané et un classement en pourcentage ne garantissent pas une équité parfaite.
- Les parcours 1/2/3 sont actuellement des groupes distincts de 8/16/36 questions ; les tronçons communs nécessitent une validation terrain avant impression.
- Le classement ne gère pas encore automatiquement la question bonus : départage **manuel** à l'arrivée, en présence de l'organisation.
- Une session est associée à un navigateur. Si une personne change d'appareil ou efface ses cookies, elle ne retrouve pas sa partie ; prévoir un identifiant récupérable pour la version finale.
- Le contrôle des doublons porte sur un galet pour une même session, pas sur les comptes multiples. Ajouter des protections antifraude et tester la charge avant usage public.
- Les réponses QCM ont été générées à partir de la banque initiale et **doivent être relues** pour vérifier leur pertinence pédagogique et les choix de réponses.
- Ne pas collecter de noms complets d'enfants dans cette version. Prévoir les mentions RGPD et les modalités d'encadrement des mineurs.

## Tests

Démarrer l'application puis ouvrir un navigateur. Inscrire un pseudonyme, choisir un itinéraire, aller dans « Voir les galets (mode test) », répondre à une question, vérifier que les points et le classement évoluent. Scanner ensuite un QR code généré avec l'adresse publique.
