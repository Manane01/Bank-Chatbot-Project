import os
import random
import pandas as pd

# Définition du chemin vers le dossier "data", situé un niveau au-dessus de ce fichier.
# Cela permet de toujours sauvegarder le dataset au bon endroit, peu importe l'endroit
# depuis lequel le script est exécuté.
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

"""
    Définition du dictionnaire des intentions du chatbot
    Chaque intention contient :
        - une catégorie (utile pour regrouper les intentions)
        - une liste d'instructions possibles (phrases utilisateur)
        - une liste de réponses associées
    Ce dictionnaire sert de base à la génération du dataset synthétique.
"""
intents = {

    "activer_carte": {
        "category": "CARTE",
        "instructions": [
            "Je dois activer ma carte bancaire.", "Où activer ma nouvelle carte ?",
            "Comment faire pour activer ma carte ?", "Je viens de recevoir ma carte, comment l'activer ?",
            "Aidez-moi à activer ma carte s'il vous plaît."
        ],
        "responses": [
            "Rendez-vous à l'agence la plus proche pour activer votre carte bancaire."
        ]
    },
    "bloquer_carte": {
        "category": "CARTE",
        "instructions": [
            "Je dois bloquer ma carte.", "Comment bloquer ma carte ?", "Ma carte est perdue, que faire ?",
            "Je veux désactiver ma carte bancaire.", "Bloquez ma carte maintenant !"
        ],
        "responses": [
            "Votre carte sera bloquée immédiatement après vérification de votre identité. "
            "Pour ce faire, connectez-vous à votre application mobile et suivez les différentes étapes. "
            "Si vous rencontrez des difficultés, vous pouvez contacter le service client ou vous rendre à l'agence."
        ]
    },
    "reactiver_carte": {
        "category": "CARTE",
        "instructions": [
            "Je dois débloquer ma carte.", "Comment débloquer ma carte ?", "Ma carte est bloquée, que faire ?",
            "Je veux réactiver ma carte bancaire.", "Débloquez ma carte maintenant !",
            "Je veux débloquer ma carte bancaire", "Ma carte bancaire n'est plus fonctionnelle"
        ],
        "responses": [
            "Connectez-vous à votre application mobile et suivez les étapes de vérification de votre identité "
            "pour réactiver votre carte instantanément. Vous pouvez également contacter le service client ou " 
            "vous rendre à l'agence la plus proche pour réactiver votre carte bancaire."
        ]
    },
    "demander_carte": {
        "category": "CARTE",
        "instructions": [
            "Je veux une nouvelle carte", "Comment obtenir une carte bancaire ?",
            "Je souhaite demander une carte", "Quelle carte puis-je avoir ?",
            "Demande de carte bancaire", "Je veux faire une demande de carte"
        ],
        "responses": [
            "Vous pouvez faire une demande de carte depuis votre espace client en ligne ou en agence. "
            "Plusieurs types de cartes sont disponibles selon votre profil."
        ]
    },
    "changer_plafond_carte": {
        "category": "CARTE",
        "instructions": [
            "Je veux augmenter le plafond de ma carte", "Comment modifier mes limites de paiement ?",
            "Mon plafond de carte est trop bas", "Augmenter le plafond de retrait",
            "Changer les limites de ma carte bancaire"
        ],
        "responses": [
            "Vous pouvez modifier les plafonds de votre carte depuis votre application mobile "
            "dans la section 'Ma carte' ou contacter votre conseiller."
        ]
    },

    "consulter_solde": {
        "category": "COMPTE",
        "instructions": [
            "Je veux consulter mon solde.", "Pouvez-vous afficher le solde de mon compte ?",
            "Combien d'argent ai-je sur mon compte ?", "Quel est le montant restant ?",
            "Montrez-moi mon solde actuel."
        ],
        "responses": [
            "Connectez-vous à l'application mobile pour voir votre solde mis à jour dans votre espace client."
        ]
    },
    "ouvrir_compte": {
        "category": "COMPTE",
        "instructions": [
            "Je souhaite ouvrir un compte bancaire.", "Comment créer un compte ?",
            "Je veux devenir client.", "Quels papiers sont nécessaires pour ouvrir un compte ?",
            "J'aimerais ouvrir un nouveau compte."
        ],
        "responses": [
            "Vous pouvez ouvrir un compte directement depuis notre site internet ou "
            "application mobile ou vous rendre à notre agence la plus proche."
        ]
    },
    "fermer_compte": {
        "category": "COMPTE",
        "instructions": [
            "Je veux fermer mon compte", "Comment clôturer mon compte bancaire ?",
            "Fermeture de compte", "Je souhaite résilier mon compte",
            "Clôturer mon compte bancaire"
        ],
        "responses": [
            "Pour fermer votre compte, vous devez vous rendre en agence avec une pièce d'identité. "
            "Assurez-vous que le solde soit nul et qu'aucune opération ne soit en cours."
        ]
    },

    "effectuer_virement": {
        "category": "TRANSACTION",
        "instructions": [
            "Je veux faire un virement", "Comment transférer de l'argent ?",
            "Virement vers un autre compte", "Transférer des fonds",
            "Faire un virement bancaire", "Envoyer de l'argent à un proche"
        ],
        "responses": [
            "Vous pouvez effectuer un virement depuis votre espace client en ligne ou l'application mobile. "
            "Renseignez les coordonnées du bénéficiaire et le montant."
        ]
    },
    "consulter_historique": {
        "category": "TRANSACTION",
        "instructions": [
            "Je veux voir mes dernières transactions", "Historique de mes opérations",
            "Montrez-moi mes derniers mouvements", "Relevé de compte récent",
            "Quelles sont mes transactions récentes ?"
        ],
        "responses": [
            "Votre historique des transactions est disponible dans votre espace client "
            "ou l'application mobile dans la section 'Mes opérations'."
        ]
    },
    "contester_transaction": {
        "category": "TRANSACTION",
        "instructions": [
            "Je veux contester une transaction", "Opération non reconnue",
            "Contester un prélèvement", "Je n'ai pas fait cette transaction",
            "Transaction frauduleuse à contester"
        ],
        "responses": [
            "Pour contester une transaction, contactez immédiatement le service client "
            "ou rendez-vous en agence avec le détail de l'opération concernée."
        ]
    },

    "demander_pret": {
        "category": "PRET",
        "instructions": [
            "Je veux faire une demande de prêt", "Comment obtenir un crédit ?",
            "Demande de prêt immobilier", "Prêt personnel",
            "Simulation de prêt", "Je souhaite emprunter"
        ],
        "responses": [
            "Vous pouvez faire une simulation de prêt en ligne ou prendre rendez-vous "
            "avec un conseiller pour étudier votre projet."
        ]
    },
    "remboursement_anticipé": {
        "category": "PRET",
        "instructions": [
            "Je veux rembourser mon prêt en avance", "Remboursement anticipé",
            "Comment solder mon crédit plus tôt ?", "Rembourser avant terme"
        ],
        "responses": [
            "Le remboursement anticipé est possible sous conditions. "
            "Contactez votre conseiller pour connaître les modalités et éventuels frais."
        ]
    },
    "taux_interet_pret": {
        "category": "PRET",
        "instructions": [
            "Quel est le taux de mon prêt ?", "Taux d'intérêt actuel",
            "Taux pour un crédit immobilier", "Conditions taux prêt"
        ],
        "responses": [
            "Les taux varient selon le type de prêt et votre profil. "
            "Consultez notre simulateur en ligne ou contactez un conseiller pour des taux personnalisés."
        ]
    },

    "ouvrir_compte_epargne": {
        "category": "EPARGNE",
        "instructions": [
            "Ouvrir un compte épargne", "Compte sur livret",
            "Je veux épargner", "Créer un compte d'épargne",
            "Livret A ou LDDS ?"
        ],
        "responses": [
            "Plusieurs solutions d'épargne sont disponibles selon vos projets. "
            "Rendez-vous en agence ou connectez-vous pour découvrir nos offres."
        ]
    },
    "taux_epargne": {
        "category": "EPARGNE",
        "instructions": [
            "Quel est le taux de mon livret ?", "Taux d'intérêt épargne",
            "Rendement compte épargne", "Taux du Livret A"
        ],
        "responses": [
            "Les taux d'épargne sont réglementés ou variables selon les produits. "
            "Consultez votre espace client pour les taux applicables à vos comptes."
        ]
    },

    "réinitialiser_mot_de_passe": {
        "category": "SECURITE",
        "instructions": [
            "Je veux changer mon mot de passe.", "Mot de passe oublié, que faire ?",
            "Je n'arrive pas à me connecter.", "Comment modifier mon mot de passe ?",
            "J'ai perdu mon mot de passe d'accès."
        ],
        "responses": [
            "Pour réinitialiser votre mot de passe, connectez-vous à votre compte depuis le site internet ou votre application mobile, "
            "allez dans les paramètres puis dans la rubrique 'Mot de passe', cliquez sur 'Mot de passe oublié'."
            "Un lien de réinitialisation sera envoyé à votre adresse email, cliquez-y et entrer un nouveau mot de passe."
            "Si vous n'y parvenez pas depuis le site ou l'application, alors veuillez vous rendre à l'agence pour vous faire assister."
        ],
    },
    "signaler_transaction_suspecte": {
        "category": "SECURITE",
        "instructions": [
            "Je constate une opération suspecte.", "Quelqu'un a débité mon compte sans autorisation.",
            "Je veux signaler un paiement non reconnu.", "Ma carte a été utilisée sans mon accord.",
            "Comment déclarer une fraude ?"
        ],
        "responses": [
            "Veuillez signaler la transaction suspecte dans votre espace sécurisé. "
            "Nous allons vérifier cette opération et prendre contact avec vous dès que possible. "
            "Vous pouvez aussi vous rendre directement à l'agence pour vous faire assister"
        ]
    },

    "virement_international": {
        "category": "INTERNATIONAL",
        "instructions": [
            "Je veux faire un virement à l'étranger", "Transfert international",
            "Envoyer de l'argent à l'étranger", "Virement vers un compte overseas"
        ],
        "responses": [
            "Les virements internationaux sont possibles depuis votre espace client. "
            "Des frais et délais supplémentaires peuvent s'appliquer."
        ]
    },
    "change_devises": {
        "category": "INTERNATIONAL",
        "instructions": [
            "Acheter des devises étrangères", "Change euro/dollar",
            "Commander des devises", "Taux de change"
        ],
        "responses": [
            "Vous pouvez commander des devises en agence ou consulter nos taux de change "
            "en ligne pour une estimation."
        ]
    },

    "probleme_connexion": {
        "category": "TECHNIQUE",
        "instructions": [
            "Je n'arrive pas à me connecter", "Problème d'accès à mon compte",
            "Application ne fonctionne pas", "Site web inaccessible",
            "Mot de passe ne marche pas"
        ],
        "responses": [
            "Vérifiez votre connexion internet et essayez de rafraîchir la page. "
            "Si le problème persiste, réinitialisez votre mot de passe ou contactez l'assistance technique."
        ]
    },
    "probleme_application": {
        "category": "TECHNIQUE",
        "instructions": [
            "L'application mobile bugue", "Problème avec l'appli bancaire",
            "L'application se ferme toute seule", "Mise à jour application"
        ],
        "responses": [
            "Assurez-vous d'avoir la dernière version de l'application. "
            "Si le problème persiste, réinstallez l'application ou contactez le support technique."
        ]
    },

    "horaires_agence": {
        "category": "INFO",
        "instructions": [
            "Quels sont vos horaires d'ouverture ?", "Quand puis-je venir à la banque ?",
            "Votre agence ferme à quelle heure ?", "Je veux connaître les horaires de votre agence.",
            "L'agence est-elle ouverte aujourd'hui ?"
        ],
        "responses": [
            "Nos agences sont ouvertes du lundi au vendredi de 8h00 à 17h30 et le samedi de 8h30 à 12h00."
            "Consultez notre site internet pour vérifier les horaires de l'agence la plus proche."
        ]
    },
    "contact_service_client": {
        "category": "INFO",
        "instructions": [
            "Comment contacter le service client ?", "Numéro de téléphone banque",
            "Support client", "Service relation client",
            "Qui appeler en cas de problème ?"
        ],
        "responses": [
            "Vous pouvez contacter notre service client au 0 800 123 456 (appel gratuit) "
            "du lundi au vendredi de 8h à 19h et le samedi de 9h à 13h."
        ]
    }
}


"""
    Génération du dataset synthétique
    Pour chaque intention, on crée un certain nombre d'exemples (total_per_intent).
    Chaque ligne générée contient :
        - un tag unique
        - une instruction (phrase utilisateur tirée au hasard)
        - une catégorie
        - l'intention
        - une réponse (tirée au hasard)
"""

data = []
tag_count = 1
total_per_intent = 500

for intent, info in intents.items():
    for _ in range(total_per_intent):
        tag = f"TAG_{tag_count:06d}"
        instruction = random.choice(info["instructions"])
        response = random.choice(info["responses"])
        category = info["category"]
        data.append([tag, instruction, category, intent, response])
        tag_count += 1

# Conversion du dataset en DataFrame Pandas
df = pd.DataFrame(data, columns=["tag", "instruction", "category", "intent", "response"])

# Sauvegarde du dataset au format CSV dans le dossier "data"
# Le fichier sera créé au chemin :
# bankApp/data/banking_dataset.csv
OUTPUT_FILE = os.path.join(DATA_DIR, "banking_dataset.csv")
df.to_csv(OUTPUT_FILE, index=False)

print(f"Dataset généré avec succès ! {len(df)} lignes créées.")
print(f"Catégories disponibles : {df['category'].unique()}")
print(f"Intentions disponibles : {df['intent'].nunique()}")

