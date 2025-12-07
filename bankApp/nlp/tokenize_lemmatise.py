import os
import pandas as pd
import spacy

# Définitions des chemins 
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "banking_dataset_clean.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "banking_dataset_tokenize.csv")

nlp = spacy.load("fr_core_news_sm")

def clean_dataset():

    """
    Lit le CSV d'entrée, nettoie et lemmatise le texte, 
    puis sauvegarde le résultat dans un nouveau CSV.
    """
    df = pd.read_csv(INPUT_FILE, encoding="utf-8")

    def tokenize_and_lemmatize(text):

        """
        Tokenise et lemmatise une phrase :
        - Supprime les stop words
        - Supprime les tokens non alphabétiques (ponctuation, chiffres)
        - Retourne une chaîne de texte nettoyée
        """

        doc = nlp(text)
        tokens = [token.lemma_ for token in doc if not token.is_stop and token.is_alpha]
        return " ".join(tokens)

    df["tokens"] = df["instruction_clean"].apply(tokenize_and_lemmatize)

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    
    return df

clean_dataset()
