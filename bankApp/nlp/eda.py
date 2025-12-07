import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter

# Configuration des chemins
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
INPUT_FILE = os.path.join(DATA_DIR, "banking_dataset_clean.csv")
OUTPUT_DIR = os.path.join(DATA_DIR, "eda_fig")

# Création du dossier de sortie
os.makedirs(OUTPUT_DIR, exist_ok=True)

def setup_plot_style():
    # Configuration du style des visualisations
    plt.style.use('default')
    sns.set_palette("husl")

def load_and_prepare_data():
    # Chargement et préparation des données
    df = pd.read_csv(INPUT_FILE, encoding='utf-8')
    
    # Calcul des longueurs de texte
    df['instruction_length'] = df['instruction_clean'].str.len()
    df['instruction_word_count'] = df['instruction_clean'].str.split().str.len()
    df['response_word_count'] = df['response'].str.split().str.len()
    
    return df

def basic_statistics(df):
    # Statistiques de base du dataset
    print("=" * 50)
    print("STATISTIQUES DE BASE DU DATASET")
    print("=" * 50)
    
    stats = {
        "Nombre total d'échantillons": len(df),
        "Nombre de catégories": df['category'].nunique(),
        "Nombre d'intentions": df['intent'].nunique(),
        "Colonnes disponibles": list(df.columns),
        "Valeurs manquantes": df.isnull().sum().to_dict(),
        "Doublons": df.duplicated().sum()
    }
    
    for key, value in stats.items():
        print(f" {key}: {value}")
        
    return stats

def category_distribution(df):
    # Distribution des catégories et intentions
    print("\n" + "=" * 50)
    print("DISTRIBUTION DES CATÉGORIES")
    print("=" * 50)
    
    # Distribution par catégorie
    category_counts = df['category'].value_counts()
    print("Distribution par catégorie:")
    for category, count in category_counts.items():
        percentage = (count / len(df)) * 100
        print(f"   {category}: {count} échantillons ({percentage:.1f}%)")
    
    # Distribution par intention
    intent_counts = df['intent'].value_counts()
    print(f"\nTop 5 des intentions:")
    for intent, count in intent_counts.head().items():
        percentage = (count / len(df)) * 100
        print(f"   {intent}: {count} échantillons ({percentage:.1f}%)")
        
    return category_counts, intent_counts

def visualize_category_distribution(df):
    # Visualisations de la distribution
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Pie chart des catégories
    category_counts = df['category'].value_counts()
    axes[0, 0].pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%', 
                  startangle=90)
    axes[0, 0].set_title('Distribution des Catégories', fontsize=14, fontweight='bold')
    
    # Bar chart des intentions (top 10)
    intent_counts = df['intent'].value_counts().head(10)
    sns.barplot(x=intent_counts.values, y=intent_counts.index, ax=axes[0, 1])
    axes[0, 1].set_title('Top 10 des Intentions', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Nombre d\'échantillons')
    
    # Histogramme de la longueur des instructions
    sns.histplot(data=df, x='instruction_length', bins=30, ax=axes[1, 0], kde=True)
    axes[1, 0].set_title('Distribution de la Longueur des Instructions', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Longueur des instructions (caractères)')
    
    # Boxplot par catégorie
    sns.boxplot(data=df, x='category', y='instruction_length', ax=axes[1, 1])
    axes[1, 1].set_title('Longueur des Instructions par Catégorie', fontsize=14, fontweight='bold')
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].set_xlabel('Catégorie')
    axes[1, 1].set_ylabel('Longueur (caractères)')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'distribution_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print("Graphiques de distribution sauvegardés")

def text_length_analysis(df):
    # Analyse de la longueur du texte
    print("\n" + "=" * 50)
    print("ANALYSE DE LA LONGUEUR DU TEXTE")
    print("=" * 50)
    
    length_stats = {
        "Instructions - Mots moyens": df['instruction_word_count'].mean(),
        "Instructions - Mots max": df['instruction_word_count'].max(),
        "Instructions - Mots min": df['instruction_word_count'].min(),
        "Réponses - Mots moyens": df['response_word_count'].mean(),
        "Réponses - Mots max": df['response_word_count'].max(),
    }
    
    for key, value in length_stats.items():
        print(f"• {key}: {value:.1f}")
        
    # Visualisation détaillée
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Distribution des mots dans les instructions
    sns.histplot(data=df, x='instruction_word_count', bins=20, ax=axes[0, 0], kde=True)
    axes[0, 0].set_title('Distribution du Nombre de Mots - Instructions')
    axes[0, 0].set_xlabel('Nombre de mots')
    axes[0, 0].axvline(df['instruction_word_count'].mean(), color='red', linestyle='--', 
                      label=f'Moyenne: {df["instruction_word_count"].mean():.1f}')
    axes[0, 0].legend()
    
    # Distribution des mots dans les réponses
    sns.histplot(data=df, x='response_word_count', bins=20, ax=axes[0, 1], kde=True)
    axes[0, 1].set_title('Distribution du Nombre de Mots - Réponses')
    axes[0, 1].set_xlabel('Nombre de mots')
    axes[0, 1].axvline(df['response_word_count'].mean(), color='red', linestyle='--', 
                      label=f'Moyenne: {df["response_word_count"].mean():.1f}')
    axes[0, 1].legend()
    
    # Mots par catégorie (instructions)
    sns.boxplot(data=df, x='category', y='instruction_word_count', ax=axes[1, 0])
    axes[1, 0].set_title('Nombre de Mots par Catégorie - Instructions')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Scatter plot longueur instructions vs réponses
    sns.scatterplot(data=df, x='instruction_word_count', y='response_word_count', alpha=0.6, ax=axes[1, 1])
    axes[1, 1].set_title('Relation: Longueur Instructions vs Réponses')
    axes[1, 1].set_xlabel('Mots dans instruction')
    axes[1, 1].set_ylabel('Mots dans réponse')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'text_length_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    return length_stats

def word_frequency_analysis(df):
    # Analyse de la fréquence des mots
    print("\n" + "=" * 50)
    print("ANALYSE DE FRÉQUENCE DES MOTS")
    print("=" * 50)
    
    # Tous les mots combinés
    all_text = ' '.join(df['instruction_clean'].dropna())
    words = all_text.split()
    word_freq = Counter(words)
    
    print("Top 20 des mots les plus fréquents:")
    for word, freq in word_freq.most_common(20):
        print(f"   '{word}': {freq} occurrences")
    
    # Word Cloud
    plt.figure(figsize=(12, 6))
    wordcloud = WordCloud(width=800, height=400, background_color='white', max_words=100).generate(all_text)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud des Instructions', size=16, fontweight='bold')
    plt.savefig(os.path.join(OUTPUT_DIR, 'wordcloud.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Top 30 mots les plus fréquents
    top_words = word_freq.most_common(30)
    words, frequencies = zip(*top_words)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x=list(frequencies), y=list(words))
    plt.title('Top 30 des Mots les Plus Fréquents', fontsize=16, fontweight='bold')
    plt.xlabel('Fréquence')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'top_words_frequency.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    return word_freq

def category_specific_analysis(df):
    # Analyse spécifique par catégorie
    print("\n" + "=" * 50)
    print("ANALYSE SPÉCIFIQUE PAR CATÉGORIE")
    print("=" * 50)
    
    categories = df['category'].unique()
    n_categories = len(categories)
    
    # Créer une grille de subplots
    n_rows = (n_categories + 2) // 3
    fig, axes = plt.subplots(n_rows, 3, figsize=(18, 5 * n_rows))
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    
    for i, category in enumerate(categories):
        row = i // 3
        col = i % 3
        
        category_text = ' '.join(df[df['category'] == category]['instruction_clean'])
        words = category_text.split()
        word_freq = Counter(words)
        
        # Top 8 mots pour cette catégorie
        top_words = word_freq.most_common(8)
        if top_words:
            words, freqs = zip(*top_words)
            
            sns.barplot(x=list(freqs), y=list(words), ax=axes[row, col])
            axes[row, col].set_title(f'Top Mots - {category}', fontweight='bold')
            axes[row, col].set_xlabel('Fréquence')
        
        print(f"\nCatégorie '{category}':")
        for word, freq in top_words[:5]:
            print(f"   '{word}': {freq}")
    
    # Cacher les axes non utilisés
    for i in range(len(categories), n_rows * 3):
        row = i // 3
        col = i % 3
        axes[row, col].set_visible(False)
        
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'category_word_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()

def intent_specific_analysis(df):
    # Analyse par intention spécifique
    print("\n" + "=" * 50)
    print("ANALYSE PAR INTENTION")
    print("=" * 50)
    
    # Sélectionner quelques intentions importantes
    important_intents = ['activer_carte', 'consulter_solde', 'demander_pret', 'probleme_connexion']
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, intent in enumerate(important_intents):
        if i < len(axes):
            intent_data = df[df['intent'] == intent]
            intent_text = ' '.join(intent_data['instruction_clean'])
            words = intent_text.split()
            word_freq = Counter(words)
            
            top_words = word_freq.most_common(6)
            if top_words:
                words, freqs = zip(*top_words)
                sns.barplot(x=list(freqs), y=list(words), ax=axes[i])
                axes[i].set_title(f'Top Mots - {intent}', fontweight='bold')
                axes[i].set_xlabel('Fréquence')
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'intent_word_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()

def generate_report():
    # Génère un rapport complet d'EDA

    # Configuration
    setup_plot_style()
    df = load_and_prepare_data()
    
    # Exécution de toutes les analyses
    basic_stats = basic_statistics(df)
    category_dist, intent_dist = category_distribution(df)
    length_stats = text_length_analysis(df)
    word_freq = word_frequency_analysis(df)
    
    # Génération des visualisations
    visualize_category_distribution(df)
    category_specific_analysis(df)
    intent_specific_analysis(df)
    
    print("\n" + "=" * 70)
    print("ANALYSE TERMINÉE - RAPPORTS SAUVEGARDÉS DANS 'data/eda_fig/'")
    print("=" * 70)
    print("Fichiers générés:")
    print("   distribution_analysis.png")
    print("   text_length_analysis.png")
    print("   wordcloud.png") 
    print("   top_words_frequency.png")
    print("   category_word_analysis.png")
    print("   intent_word_analysis.png")
    print("\nPoints clés à retenir:")
    print(f"   Dataset équilibré entre {len(category_dist)} catégories")
    print(f"   {basic_stats['Nombre total d\'échantillons']} échantillons au total")
    print(f"   Longueur moyenne des instructions: {length_stats['Instructions - Mots moyens']:.1f} mots")

# Point d'entrée principal
if __name__ == "__main__":
    generate_report()