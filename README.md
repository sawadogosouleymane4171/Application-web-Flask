# Application Web Flask

Cette application web est développée avec Flask et permet de gérer des utilisateurs, effectuer des calculs spécifiques et visualiser des résultats. Elle est prête à être déployée sur Render.

## Fonctionnalités
- **Inscription et connexion des utilisateurs**.
- **Réinitialisation du mot de passe** via email.
- **Calculs personnalisés** avec enregistrement des résultats.
- **Visualisation graphique** des données calculées.
- **Gestion des logs d'activité des utilisateurs**.

## Prérequis
- Python 3.8 ou supérieur.
- Un environnement virtuel Python (`venv`).
- Les dépendances listées dans `requirements.txt`.

## Installation locale
1. Clonez le dépôt GitHub :
   ```bash
   git clone https://github.com/<votre-utilisateur>/<votre-repo>.git
   cd <votre-repo>
   ```

2. Activez l'environnement virtuel :
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez les variables d'environnement :
   - Créez un fichier `.env` à la racine du projet en suivant l'exemple fourni dans `.env.example`.

5. Lancez l'application :
   ```bash
   python app.py
   ```

6. Accédez à l'application dans votre navigateur à l'adresse :
   ```
   http://127.0.0.1:5000
   ```

## Déploiement sur Render
1. Poussez le projet sur GitHub.
2. Connectez votre dépôt à Render.
3. Configurez les variables d'environnement sur Render.
4. Déployez l'application.

## Structure du projet
```
last/
├── app.py                 # Fichier principal de l'application
├── requirements.txt       # Dépendances Python
├── Procfile               # Fichier pour le déploiement sur Render
├── .env.example           # Exemple de configuration des variables d'environnement
├── migrations/            # Scripts de migration de la base de données
├── instance/              # Contient la base de données SQLite (ignorée par Git)
├── static/                # Fichiers statiques (CSS, JS, images)
├── templates/             # Fichiers HTML pour les pages web
└── README.md              # Documentation du projet
```

## Fonctionnalités principales
- **Inscription et connexion** :
  - Les utilisateurs peuvent s'inscrire avec un email et un mot de passe.
  - Connexion sécurisée avec hachage des mots de passe.

- **Réinitialisation du mot de passe** :
  - Envoi d'un code de vérification par email pour réinitialiser le mot de passe.

- **Calculs personnalisés** :
  - Les utilisateurs peuvent effectuer des calculs et enregistrer les résultats.

- **Visualisation graphique** :
  - Génération de graphiques basés sur les données calculées.

## Technologies utilisées
- **Backend** : Flask, Flask-SQLAlchemy, Flask-Migrate.
- **Frontend** : HTML, CSS, Bootstrap.
- **Base de données** : SQLite.
- **Autres** : Flask-Mail pour l'envoi d'emails, Matplotlib pour les graphiques.

## Auteur
- **Nom** : Souleymane Sawadogo
- **Email** : sawadogo.souleymane4171.fsts@uhp.ac.ma

## Licence
Ce projet est sous licence MIT. Vous êtes libre de l'utiliser, de le modifier et de le distribuer.
