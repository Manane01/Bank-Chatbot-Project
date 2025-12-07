#bankApp/nlp/model_training.py
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sentence_transformers import SentenceTransformer

# Configuration des chemins
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(DATA_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def train_models():
    """
    Entraîne et sauvegarde tous les modèles
    Returns:
        tuple: (tfidf, rfc, model_embed, df, embeddings, categories)
    """

    # Chargement du dataset
    INPUT_FILE = os.path.join(DATA_DIR, "banking_dataset_tokenize.csv")
    df = pd.read_csv(INPUT_FILE, encoding="utf-8")
    print(f"Données chargées: {len(df)} échantillons")

    # Entraînement TF-IDF & RandomForest
    print("Entraînement TF-IDF et Random Forest...")
    tfidf = TfidfVectorizer()
    X_tfidf = tfidf.fit_transform(df["tokens"])
    y = df["category"]
    
    # Split des données
    X_train, X_test, y_train, y_test = train_test_split(
        X_tfidf, y, test_size=0.2, random_state=42
    )

    # Entraînement Random Forest
    rfc = RandomForestClassifier()
    rfc.fit(X_train, y_train)
    print("Random Forest entraîné")

    # Génération des embeddings
    print("Génération des embeddings...")
    model_embed = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = model_embed.encode(df["instruction_clean"].tolist())
    categories = df["category"].values
    print("Embeddings générés")

    # Sauvegarde des modèles
    print("Sauvegarde des modèles...")
    joblib.dump(tfidf, os.path.join(MODEL_DIR, 'tfidf_vectorizer.joblib'))
    joblib.dump(rfc, os.path.join(MODEL_DIR, 'random_forest.joblib'))
    joblib.dump(model_embed, os.path.join(MODEL_DIR, 'sentence_transformer.joblib'))
    
    # Sauvegarde des embeddings et metadata
    np.save(os.path.join(MODEL_DIR, 'embeddings.npy'), embeddings)
    df.to_csv(os.path.join(MODEL_DIR, 'dataset_metadata.csv'), index=False)
    
    return tfidf, rfc, model_embed, df, embeddings, categories

def load_trained_models():
    """
    Charge les modèles pré-entraînés
    Returns:
        tuple: (tfidf, rfc, model_embed, df, embeddings, categories)
    """
    
    try:
        tfidf = joblib.load(os.path.join(MODEL_DIR, 'tfidf_vectorizer.joblib'))
        rfc = joblib.load(os.path.join(MODEL_DIR, 'random_forest.joblib'))
        model_embed = joblib.load(os.path.join(MODEL_DIR, 'sentence_transformer.joblib'))
        
        df = pd.read_csv(os.path.join(MODEL_DIR, 'dataset_metadata.csv'))
        embeddings = np.load(os.path.join(MODEL_DIR, 'embeddings.npy'))
        categories = df["category"].values
        
        print("Modèles chargés avec succès!")
        return tfidf, rfc, model_embed, df, embeddings, categories
        
    except FileNotFoundError as e:
        print(f"Erreur: Modèles non trouvés. Veuillez d'abord exécuter l'entraînement.")
        print(f"Détail: {e}")
        return None

if __name__ == "__main__":
    # Exécute l'entraînement si le script est lancé directement
    train_models()