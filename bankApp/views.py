from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from bankApp import app, db_manager
from bankApp.nlp.preduction_service import get_response, DEFAULT_RESPONSE
from config import Config
import uuid

# Configuration Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'error'

class User:
    def __init__(self, user_data):
        self.id = user_data['public_id']
        self.email = user_data['email']
        self.first_name = user_data['first_name']
        self.last_name = user_data['last_name']
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return self.id

@login_manager.user_loader
def load_user(public_id):
    user_data = db_manager.get_user_by_public_id(public_id)
    if user_data:
        return User(user_data)
    return None

# Routes d'authentification
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_data = db_manager.authenticate_user(email, password)
        if user_data:
            user = User(user_data)
            login_user(user)
            
            next_page = request.args.get('next')
            flash(f'Bienvenue {user.first_name} !', 'success')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Email ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validation basique
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères.', 'error')
            return render_template('register.html')
        
        user_data = db_manager.create_user(email, password, first_name, last_name)
        if user_data:
            flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Un compte avec cet email existe déjà.', 'error')
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('index'))

# Routes protégées
@app.route('/dashboard')
@login_required
def dashboard():
    user_data = db_manager.get_user_by_public_id(current_user.id)
    return render_template('dashboard.html', user=user_data)

@app.route('/profile')
@login_required
def profile():
    user_data = db_manager.get_user_by_public_id(current_user.id)
    return render_template('profile.html', user=user_data)

@app.route('/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html')

@app.route('/historique')
@login_required
def historique():
    user_data = db_manager.get_user_by_public_id(current_user.id)
    conversations = db_manager.get_conversation_history(user_data['id'])
    
    categories = set()
    for conv in conversations:
        if conv['category'] and conv['category'] != 'Inconnu':
            categories.add(conv['category'])
    
    categories = sorted(list(categories))
    
    return render_template('historique.html', 
                         conversations=conversations, 
                         categories=categories)

# API modifiée pour inclure l'utilisateur
@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    user_message = request.json.get('message', '').strip()
    
    if not user_message:
        return jsonify({'error': 'Message vide'}), 400
    
    try:
        user_data = db_manager.get_user_by_public_id(current_user.id)
        category, intent, response, score = get_response(
            user_message, 
            min_score=Config.NLP_MIN_CONFIDENCE
        )
        
        if response is None:
            final_response = DEFAULT_RESPONSE
            category = "Inconnue"
            confidence = None
        else:
            final_response = response
            confidence = score
        
        # Sauvegarde avec user_id
        db_manager.save_conversation(
            user_data['id'],
            user_message, 
            final_response, 
            category, 
            confidence
        )
        
        return jsonify({
            'response': final_response,
            'category': category,
            'confidence': round(confidence, 2) if confidence else 0,
            'success': True
        })
        
    except Exception as e:
        print(f"Erreur traitement NLP: {e}")
        return jsonify({
            'response': "Désolé, une erreur s'est produite. Veuillez réessayer.",
            'category': "Erreur",
            'confidence': 0.0,
            'success': False
        }), 500

# Route publique
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')