import os
import pandas as pd
import re

# Définir les chemins
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "banking_dataset.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "banking_dataset_clean.csv")

# Charger le dataset
df = pd.read_csv(INPUT_FILE)

# Fonction pour nettoyer le texte
def remove_ponctuation(text):
    
    # Convertir le texte en minuscule
    text = text.lower()
    
    # Supprimer la ponctuation et caractères spéciaux
    text = re.sub(r"[^a-z0-9àâçéèêëîïôûù]", " ", text)

    # Supprimer les espaces multiples
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

# Appliquer la fonction
df["instruction_clean"] = df["instruction"].apply(remove_ponctuation)

# Sauvegarder dans un nouveau fichier CSV
df.to_csv(OUTPUT_FILE, index=False)

  
print(df)