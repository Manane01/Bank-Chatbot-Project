from flask import Flask
from config import Config
from bankApp.models import DatabaseManager

app  = Flask(__name__)
app.config.from_object(Config)

# Gestionnaire de base de données
db_manager = DatabaseManager()

# Iniitialisation de la DB
db_manager.init_db()

# Import des routes après la création de app
from bankApp import views


