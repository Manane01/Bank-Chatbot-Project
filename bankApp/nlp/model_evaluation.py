import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.model_selection import cross_val_score, train_test_split
from model_training import load_trained_models

# Configuration des chemins
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
MODEL_DIR = os.path.join(DATA_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def plot_confusion_matrix(y_test, y_pred, categories):
    # Visualisation de la matrice de confusion
    cm = confusion_matrix(y_test, y_pred)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
               xticklabels=categories, 
               yticklabels=categories,
               cbar_kws={'shrink': 0.8})
    plt.title('Matrice de Confusion - Classification des Catégories', 
             fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Prédictions', fontsize=12)
    plt.ylabel('Vérités Terrain', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, 'confusion_matrix.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("Matrice de confusion sauvegardée")

def plot_feature_importance(model, vectorizer, top_n=20):
    # Importance des features (TF-IDF)
    feature_names = vectorizer.get_feature_names_out()
    importances = model.feature_importances_
    
    # Top N features
    indices = np.argsort(importances)[::-1][:top_n]
    top_features = [feature_names[i] for i in indices]
    top_importances = importances[indices]
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x=top_importances, y=top_features)
    plt.title(f'Top {top_n} des Features les plus Importantes (TF-IDF)', 
             fontsize=16, fontweight='bold')
    plt.xlabel('Importance', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, 'feature_importance.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Importance des features sauvegardée")

def plot_cross_validation(cv_scores):
    # Visualisation des scores de validation croisée
    plt.figure(figsize=(10, 6))
    x_pos = np.arange(len(cv_scores))
    bars = plt.bar(x_pos, cv_scores, color=sns.color_palette("viridis", len(cv_scores)))
    plt.axhline(y=cv_scores.mean(), color='red', linestyle='--', 
               label=f'Moyenne: {cv_scores.mean():.4f}')
    plt.xlabel('Fold de Validation')
    plt.ylabel('Accuracy')
    plt.title('Scores de Validation Croisée', fontsize=16, fontweight='bold')
    plt.xticks(x_pos, [f'Fold {i+1}' for i in range(len(cv_scores))])
    plt.legend()
    
    # Ajouter les valeurs sur les barres
    for bar, score in zip(bars, cv_scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                f'{score:.4f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(os.path.join(MODEL_DIR, 'cross_validation_scores.png'), dpi=300, bbox_inches='tight')
    plt.close()

def comprehensive_evaluation(model, vectorizer, X_test, y_test, categories):
    # Évaluation complète du modèle
    print("=" * 60)
    print("ÉVALUATION COMPLÈTE DU MODÈLE")
    print("=" * 60)
    
    # Prédictions
    y_pred = model.predict(X_test)
    
    # Accuracy de base
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    
    # Rapport de classification détaillé
    print("\nRAPPORT DE CLASSIFICATION:")
    print(classification_report(y_test, y_pred, target_names=categories))
    
    # Matrice de confusion
    plot_confusion_matrix(y_test, y_pred, categories)
    
    # Feature importance (pour Random Forest)
    if hasattr(model, 'feature_importances_'):
        plot_feature_importance(model, vectorizer)
    
    # Validation croisée
    print(f"\nVALIDATION CROISÉE (5-fold):")
    cv_scores = cross_val_score(model, X_test, y_test, cv=5, scoring='accuracy')
    
    print(f"   Scores: {[f'{score:.4f}' for score in cv_scores]}")
    print(f"   Moyenne: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    plot_cross_validation(cv_scores)
    
    return accuracy

def integrate_evaluation():
    # Charge les modèles pré-entraînés
    result = load_trained_models()
    if result is None:
        print("Impossible de charger les modèles. Entraînement nécessaire.")
        return
    
    tfidf, rfc, model_embed, df, embeddings, categories = result

    # Préparer les données pour l'évaluation
    X = tfidf.transform(df["tokens"])
    y = df["category"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Évaluation complète
    accuracy = comprehensive_evaluation(rfc, tfidf, X_test, y_test, df['category'].unique())
    
    print(f"\nPerformance finale du modèle: {accuracy:.4f}")

# Point d'entrée principal
if __name__ == "__main__":
    integrate_evaluation()