Pour pouvoir exécuter le projet, il faut :

    1. Activer l'environnement virtuel bank_env en faisant : bank_env/Scripts/activate (Sur windows)
    2. Exécuter le pipeline NLP pour s'assurer que tout fonctionne. Il faut exécuter les fichiers dans l'ordre suivant :
        a. python bankApp/nlp/data_generation.py (Pour générer le dataset)
        b. python bankApp/nlp/ponctuations.py
        c. python bankApp/nlp/eda.py
        d. python bankApp/nlp/tokenize_lemmatise.py
        e. python bankApp/nlp/model_training.py
        f. python bankApp/nlp/model_evaluation.py
        g. python bankApp/nlp/preduction_service.py
    
    3. Après avoir exécuter les fichiers NLP, on peut exécuter l'application en faisant : python run.py


    Pour créer un nouveau environnement virtuel, on procède comme suit :
    1. Créer l'environnemet virtuel en faisant : python -m venv nom_environnement_virtuel  (Sur windows)
    2. Activer l'environnement virtuel en faisant : nom_environnement_virtuel/Scripts/activate (Sur windows)
    3. Installer les dépendances en faisant : pip install -r requirements.txt
    4. Exécuter les fichiers comme précedemment