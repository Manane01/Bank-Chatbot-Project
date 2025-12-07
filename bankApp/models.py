import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from datetime import datetime
import uuid

# Classe pour gérer la connexion à la base de données, les utilisateurs et les conversations
class DatabaseManager:
    # Constructeur : initialise la configuration de la base de données
    def __init__(self):
        self.config = Config.DB_CONFIG
    
    # Établit une connexion à la base de données PostgreSQL. Retourne l'objet connexion ou None en cas d'erreur.
    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except Exception as e:
            print(f"Erreur de connexion à la base de données: {e}")
            return None
    
   # Initialise la base de données en créant les tables 'users' et 'conversations' si elles n'existent pas. 
   # Retourne True si succès, False sinon.
    def init_db(self):
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor() # Créer un curseur pour exécuter des requêtes SQL sur la connexion ouverte
            
            # Table des utilisateurs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    public_id VARCHAR(100) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    password_hash VARCHAR(200) NOT NULL,
                    first_name VARCHAR(100),
                    last_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Table des conversations
            cur.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    user_message TEXT NOT NULL,
                    bot_response TEXT NOT NULL,
                    category VARCHAR(100),
                    confidence FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit() # Enregistre les modifications dans la base de données
            cur.close() # Ferme le curseur
            conn.close() # Ferme la connexion à la base de données
            print("Base de données initialisée avec succès")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'initialisation: {e}")
            return False


    # Gestion des utilisateurs

    """
        Crée un nouvel utilisateur dans la base.
        Vérifie si l'email existe déjà, hache le mot de passe.
        Retourne un dictionnaire avec les informations de l'utilisateur ou None en cas d'erreur.
    """
    def create_user(self, email, password, first_name, last_name):
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor() # Créer un curseur pour exécuter les requêtes SQL sur la connexion ouvertes
            
            # Vérifier si l'email existe déjà
            cur.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cur.fetchone():
                return None  # Email déjà utilisé
            
            # Créer nouvel utilisateur
            public_id = str(uuid.uuid4())   # ID public unique
            password_hash = generate_password_hash(password)  # Hash du mot de passe
            
            cur.execute("""
                INSERT INTO users (public_id, email, password_hash, first_name, last_name)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, public_id, email, first_name, last_name
            """, (public_id, email, password_hash, first_name, last_name))
            
            user_data = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            # Retourne les infos essentielles de l'utilisateur
            return {
                'id': user_data[0],
                'public_id': user_data[1],
                'email': user_data[2],
                'first_name': user_data[3],
                'last_name': user_data[4]
            }
            
        except Exception as e:
            print(f"Erreur création utilisateur: {e}")
            return None
    

    """
        Authentifie un utilisateur avec son email et mot de passe.
        Met à jour la date de dernière connexion si succès.
        Retourne les infos de l'utilisateur ou None si échec.
    """
    def authenticate_user(self, email, password):
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor() # Créer un curseur pour exécuter des requêtes SQL sur la connexion ouverte
            cur.execute("""
                SELECT id, public_id, email, password_hash, first_name, last_name 
                FROM users 
                WHERE email = %s AND is_active = TRUE
            """, (email,))
            
            user = cur.fetchone() # Récupère la première ligne du résultat de la requête SQL
            if not user:
                return None
            
            # Vérification du mot de passe
            if check_password_hash(user[3], password):
                # Mis à jour la dernière connexion
                cur.execute("""
                    UPDATE users SET last_login = %s WHERE id = %s
                """, (datetime.now(), user[0]))
                conn.commit()  # Valide toutes les modifications effectuées sur la base de données
                
                return {
                    'id': user[0],
                    'public_id': user[1],
                    'email': user[2],
                    'first_name': user[4],
                    'last_name': user[5]
                }
            
            return None
            
        except Exception as e:
            print(f"Erreur authentification: {e}")
            return None
    

    """
        Récupère un utilisateur à partir de son public_id.
        Retourne un dictionnaire avec les informations utilisateur ou None si inexistant.
    """
    def get_user_by_public_id(self, public_id):
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor() # Crée un curseur pour exécuter des requêtes SQL sur la connexion ouverte
            cur.execute("""
                SELECT id, public_id, email, first_name, last_name, created_at, last_login
                FROM users 
                WHERE public_id = %s AND is_active = TRUE
            """, (public_id,))
            
            user = cur.fetchone() # Récupère la première ligne du résultat de la requête SQL
            if not user:
                return None
            
            return {
                'id': user[0],
                'public_id': user[1],
                'email': user[2],
                'first_name': user[3],
                'last_name': user[4],
                'created_at': user[5],
                'last_login': user[6]
            }
            
        except Exception as e:
            print(f"Erreur récupération utilisateur: {e}")
            return None

    # Gestion des conversations 

    """
        Sauvegarde une conversation dans la table 'conversations'.
        Retourne True si succès, False sinon.
    """
    def save_conversation(self, user_id, user_message, bot_response, category, confidence):
        conn = self.get_connection()
        if not conn:
            return False
        
        try:
            cur = conn.cursor() # Crée un curseur pour exécuter des requêtes SQL sur la connexion ouverte
            cur.execute("""
                INSERT INTO conversations (user_id, user_message, bot_response, category, confidence, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, user_message, bot_response, category, confidence, datetime.now()))
            
            conn.commit() # Valide les changements effectués dans la base de données
            cur.close() # Ferme le curseur
            conn.close() # Ferme la connexion à la base de données
            return True
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False

    """
        Récupère l'historique des conversations pour un utilisateur.
        Retourne une liste de dictionnaires contenant messages, catégorie, confiance et timestamp.
        Limite par défaut à 100 conversations.
    """
    def get_conversation_history(self, user_id, limit=100):
        conn = self.get_connection()
        if not conn:
            return []
        
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT user_message, bot_response, category, confidence, timestamp
                FROM conversations 
                WHERE user_id = %s
                ORDER BY timestamp DESC 
                LIMIT %s
            """, (user_id, limit))
            
            conversations = cur.fetchall() # Récupère toutes les lignes retournées par la requête SQL sous forme de liste de tuples
            cur.close() # Ferme le curseur
            conn.close() # Ferme la connexion à la base de données
            
            # Conversion en liste de dictionnaires
            return [{
                'user_message': conv[0],
                'bot_response': conv[1],
                'category': conv[2],
                'confidence': conv[3],
                'timestamp': conv[4].strftime('%d/%m/%Y %H:%M:%S')
            } for conv in conversations]
            
        except Exception as e:
            print(f"Erreur lors de la récupération de l'historique: {e}")
            return []