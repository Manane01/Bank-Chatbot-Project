import os
import pandas as pd
import numpy as np
from spellchecker import SpellChecker
from sklearn.metrics.pairwise import cosine_similarity
import sys
import os

# Déterminer le bon chemin d'importation
try:
    # Essayer l'import absolu d'abord
    from bankApp.nlp.model_training import load_trained_models
except ImportError:
    # Sinon, essayer l'import relatif
    from model_training import load_trained_models

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(DATA_DIR, "models")

# Correcteur orthographique
spell = SpellChecker(language='fr')

# Réponse par défaut
DEFAULT_RESPONSE = "Je n'ai pas compris votre question, pouvez-vous reformuler ?"

# Variables globales pour stocker les modèles et données
tfidf = None
rfc = None
model_embed = None
df = None
embeddings = None
categories = None
models_loaded = False

def initialize_prediction_service():
    # Initialise les modèles et données nécessaires pour les prédictions
    
    global tfidf, rfc, model_embed, df, embeddings, categories, models_loaded
    
    print("Initialisation du service de prédiction...")
    
    models = load_trained_models()
    if models is None:
        raise Exception("Impossible de charger les modèles. Exécutez d'abord l'entraînement.")
    
    tfidf, rfc, model_embed, df, embeddings, categories = models
    models_loaded = True
    print("Service de prédiction initialisé!")

def correct_text(text):
    """
    Correction orthographique du texte
    """
    words = text.split()
    corrected_words = []
    for w in words:
        correction = spell.correction(w)
        corrected_words.append(correction if correction is not None else w)
    return " ".join(corrected_words)

def get_response(question, top_n=1, min_score=0.6):
    """
    Traite une question utilisateur et retourne la réponse appropriée.
    
    Args:
        question (str): Question posée par l'utilisateur
        top_n (int): Nombre de réponses à retourner
        min_score (float): Score de similarité minimum (0.0-1.0)
        
    Returns:
        tuple: (catégorie_prédite, intention_détectée, réponse, score_confiance)
    """
    global tfidf, rfc, model_embed, df, embeddings, categories, models_loaded
    
    if not models_loaded:
        initialize_prediction_service()
    
    # Correction orthographique
    question_clean = correct_text(question)

    # Prédiction de la catégorie avec TF-IDF + Random Forest
    vec = tfidf.transform([question_clean])
    predicted_category = rfc.predict(vec)[0]

    # Filtrage des instructions par catégorie prédite
    idx = np.where(categories == predicted_category)[0]
    if len(idx) == 0:
        return predicted_category, None, None, 0.0

    category_embeddings = embeddings[idx]

    # Recherche de similarité avec les embeddings
    question_vec = model_embed.encode([question_clean])
    sims = cosine_similarity(question_vec, category_embeddings)[0]

    # Identification de l'intention la plus proche
    best_idx = sims.argmax()
    best_score = sims[best_idx]

    if best_score < min_score:
        return predicted_category, None, None, best_score

    df_index = idx[best_idx]
    predicted_intent = df.iloc[df_index]["intent"]
    response = df.iloc[df_index]["response"]

    return predicted_category, predicted_intent, response, float(best_score)

def chat_interface():
    # Interface de chat interactive
    print("\n" + "=" * 50)
    print("CHATBOT BANCAIRE - Tapez 'quit' pour quitter")
    print("=" * 50)
    
    while True:
        try:
            question = input("\nVous: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q', 'au revoir']:
                print("Au revoir !")
                break
                
            if not question:
                continue
            
            # Prédiction
            response, score = get_response(question)
            
            if response:
                print(f"Assistant [Niveau de confiance: {score:.2f}]: {response}")
            else:
                print(f"Assistant: {DEFAULT_RESPONSE}")
                
        except KeyboardInterrupt:
            print("\nInterruption - Au revoir !")
            break
        except Exception as e:
            print(f"Erreur: {e}")
            print(f"Assistant: {DEFAULT_RESPONSE}")


if __name__ == "__main__":
    # Mode démonstration
    initialize_prediction_service()
    
    # Lancement du chat interactif
    chat_interface()
    