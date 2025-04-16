import os
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Utilisation du backend Agg pour matplotlib
import matplotlib.pyplot as plt
from random import randint
from flask_migrate import Migrate
from dotenv import load_dotenv
load_dotenv()
print("DATABASE_URL =", os.getenv('DATABASE_URL'))

# Vérifiez et créez le dossier 'instance' si nécessaire
instance_path = os.path.join(os.getcwd(), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

# Vérifiez que le chemin de la base de données est accessible
db_path = os.path.join(instance_path, 'site.db')
if not os.access(instance_path, os.W_OK):
    raise PermissionError(f"Le dossier {instance_path} n'est pas accessible en écriture.")

# Assurez-vous que le fichier calculs.py existe et contient la fonction attendue
from calculs import calculer_coefficient_diffusion

# -------------------- Configuration de l'application --------------------
app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Configuration de la base de données avec un chemin absolu
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f"sqlite:///{db_path}")  # Utilisation de SQLite par défaut
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration du serveur mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'ton.email@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'ton_mot_de_passe')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'ton.email@gmail.com')  # Ajout de l'expéditeur par défaut

# -------------------- Initialisation des extensions --------------------
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
migrate = Migrate(app, db)

# -------------------- Modèles de données --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    reset_time = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.date_created}')"

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ActivityLog('{self.user_id}', '{self.activity}', '{self.timestamp}')"

# -------------------- Fonction de création de la base de données --------------------
def create_db():
    try:
        # Création du dossier instance s'il n'existe pas
        os.makedirs(app.instance_path, exist_ok=True)
        print(f"Dossier instance vérifié/créé : {app.instance_path}")

        # Création de la base de données et des tables
        with app.app_context():
            db.create_all()  # Crée toutes les tables définies dans les modèles
            print("Base de données et tables créées avec succès!")
    except Exception as e:
        print(f"Erreur lors de la création de la base de données : {e}")

# -------------------- Initialisation du fichier CSV --------------------
CSV_FILE = os.path.join(app.root_path, 'static', 'resultats_diffusion.csv')

def init_csv():
    """Vérifie si le fichier CSV existe, sinon le crée avec les colonnes nécessaires."""
    static_folder = os.path.join(app.root_path, 'static')
    os.makedirs(static_folder, exist_ok=True)  # S'assurer que le dossier static existe
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['X_A', 'D_AB'])
        df.to_csv(CSV_FILE, index=False)
        print(f"Fichier CSV créé : {CSV_FILE}")

init_csv()

# -------------------- Routes principales --------------------
@app.route('/')
def home():
    return render_template('index.html')  # Page d'accueil

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Vérifier si le nom d'utilisateur ou l'email est déjà utilisé
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Cet utilisateur existe déjà. Veuillez vous connecter.", "warning")
            return redirect(url_for('login'))

        if password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template('register.html')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Votre compte a été créé avec succès!', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username

            # Enregistrer l'activité de connexion
            log = ActivityLog(user_id=user.id, activity="Connexion réussie")
            db.session.add(log)
            db.session.commit()

            flash('Vous êtes maintenant connecté!', 'success')
            return redirect(url_for('unifac_method'))

        flash('Échec de la connexion. Vérifiez votre email et votre mot de passe.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        activity = ActivityLog(user_id=session['user_id'], activity="Déconnexion")
        db.session.add(activity)
        db.session.commit()
    session.clear()
    flash('Vous êtes déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/reset_request', methods=['GET', 'POST'])
def reset_request():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Génération d'un code de vérification aléatoire
            verification_code = randint(100000, 999999)
            session['verification_code'] = verification_code
            session['reset_email'] = email

            # Envoi du code par email
            msg = Message('Code de vérification pour réinitialisation',
                          sender=app.config['MAIL_USERNAME'],  # Utiliser MAIL_USERNAME comme expéditeur
                          recipients=[email])
            msg.body = f"Votre code de vérification est : {verification_code}"
            mail.send(msg)

            flash('Un code de vérification a été envoyé à votre adresse email.', 'info')
            return redirect(url_for('verify_code'))
        flash('Aucun utilisateur trouvé avec cette adresse email.', 'danger')

    return render_template('reset_request.html')

@app.route('/verify_code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        code = request.form.get('code')

        if 'verification_code' in session and int(code) == session['verification_code']:
            email = session.get('reset_email')
            user = User.query.filter_by(email=email).first()
            if user:
                s = Serializer(app.config['SECRET_KEY'])
                token = s.dumps({'user_id': user.id})  # Génération du token
                flash('Code vérifié avec succès. Vous pouvez maintenant réinitialiser votre mot de passe.', 'success')
                return redirect(url_for('reset_password', token=token))

        flash('Code de vérification invalide.', 'danger')

    return render_template('verify_code.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token, max_age=600)  # Le token est valable 10 minutes
    except Exception as e:
        flash('Le token est invalide ou a expiré.', 'danger')
        return redirect(url_for('reset_request'))

    user = User.query.get(data['user_id'])
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return render_template('reset_password.html', token=token)

        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = hashed_password
        user.reset_time = datetime.utcnow()
        db.session.commit()

        activity = ActivityLog(user_id=user.id, activity="Réinitialisation du mot de passe")
        db.session.add(activity)
        db.session.commit()

        flash('Mot de passe réinitialisé avec succès!', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

@app.route('/unifac_method')
def unifac_method():
    if 'user_id' not in session:
        flash('Veuillez vous connecter pour accéder à cette page', 'warning')
        return redirect(url_for('login'))
    return render_template('unifac_method.html', username=session['username'])

# -------------------- Route de calcul --------------------
@app.route('/calcul', methods=['GET', 'POST'])
def calcul():
    if request.method == 'POST':
        try:
            # Récupérer et convertir les données du formulaire en float
            data = {key: float(request.form[key]) for key in request.form}

            # Vérifier que toutes les valeurs sont positives
            if any(value <= 0 for value in data.values()):
                flash("Toutes les valeurs doivent être positives.", "danger")
                return redirect(url_for('calcul'))

            # Effectuer le calcul via la fonction importée
            D_AB, erreur_relative = calculer_coefficient_diffusion(
                data['D_AB_initial'], data['D_BA_initial'], data['fraction_A'],
                data['coef_lambda_A'], data['coef_lambda_B'], data['q_A'], data['q_B'],
                data['theta_A'], data['theta_B'], data['theta_BA'], data['theta_AB'],
                data['theta_AA'], data['theta_BB'], data['tau_AB'], data['tau_BA'], data['D_exp']
            )

            # Ajout ou mise à jour du fichier CSV pour le traçage
            if os.path.exists(CSV_FILE):
                df = pd.read_csv(CSV_FILE)
                if not df[df['X_A'] == data['fraction_A']].empty:
                    flash("Calcul existant.", "info")
                else:
                    new_row = {'X_A': data['fraction_A'], 'D_AB': D_AB}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(CSV_FILE, index=False)
                    flash("Calcul effectué avec succès !", "success")
            else:
                df = pd.DataFrame(columns=['X_A', 'D_AB'])
                new_row = {'X_A': data['fraction_A'], 'D_AB': D_AB}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_csv(CSV_FILE, index=False)
                flash("Calcul effectué avec succès !", "success")

            # Sauvegarder les résultats dans la session
            session['D_AB'] = D_AB
            session['erreur_relative'] = erreur_relative

            # Enregistrer l'activité de calcul
            activity = ActivityLog(user_id=session['user_id'], activity="Calcul effectué")
            db.session.add(activity)
            db.session.commit()

            return redirect(url_for('resultat'))

        except ValueError:
            flash("Entrées invalides. Veuillez saisir des valeurs numériques.", "danger")
            return redirect(url_for('calcul'))

    return render_template('calcul.html')

@app.route('/reset_data', methods=['POST'])
def reset_data():
    # Réinitialisation du fichier CSV
    if os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=['X_A', 'D_AB'])
        df.to_csv(CSV_FILE, index=False)
        flash("Les données ont été réinitialisées avec succès.", "success")
    else:
        flash("Aucune donnée à réinitialiser.", "warning")
    return redirect(url_for('resultat'))

@app.route('/resultat')
def resultat():
    # Vérifier que les résultats existent en session
    if 'D_AB' not in session or 'erreur_relative' not in session:
        flash("Aucun résultat trouvé. Effectuez un calcul d'abord.", "danger")
        return redirect(url_for('calcul'))

    # Chargement des données CSV pour le traçage
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        courbe_data = df.to_dict(orient='records')
    else:
        courbe_data = []

    return render_template('resultat.html', 
                           D_AB=session['D_AB'], 
                           erreur_relative=session['erreur_relative'], 
                           courbe_data=courbe_data)

@app.route('/visualiser_courbe')
def visualiser_courbe():
    try:
        df = pd.read_csv(CSV_FILE)
        if df.empty:
            flash("Aucune donnée disponible pour générer la courbe.", "warning")
            return render_template('visualiser_courbe.html', plot_path=None)
    except Exception as e:
        flash("Erreur lors de la lecture des données : " + str(e), "danger")
        return render_template('visualiser_courbe.html', plot_path=None)

    # S'assurer que le dossier static existe
    static_folder = os.path.join(app.root_path, 'static')
    os.makedirs(static_folder, exist_ok=True)

    # Générer la courbe
    plt.figure(figsize=(8, 6))
    plt.plot(df['X_A'], df['D_AB'], marker='o', color='b', label='D_AB vs X_A')
    plt.xlabel('Fraction molaire de A (X_A)')
    plt.ylabel('D_AB')
    plt.title('Courbe de D_AB en fonction de X_A')
    plt.legend()
    plt.grid(True)

    plot_path = os.path.join(static_folder, 'courbe_DAB_XA.png')
    plt.savefig(plot_path)
    print(f"Courbe générée : {plot_path}")
    plt.close()

    return render_template('visualiser_courbe.html', plot_path='static/courbe_DAB_XA.png')

@app.errorhandler(404)
def page_not_found(e):
    flash("La page que vous recherchez n'existe pas.", "danger")
    return redirect(url_for('home'))

# -------------------- Lancement de l'application --------------------
if __name__ == '__main__':
    # Création du dossier instance et de la base de données
    with app.app_context():
        create_db()
    # Utiliser le port 5000 par défaut pour l'exécution locale
    port = int(os.getenv('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
