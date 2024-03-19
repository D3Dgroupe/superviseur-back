# app/models/__init__.py
import os
from colorama import Fore
from dotenv import load_dotenv
from .base import Database

# On appelle load_dotenv() pour les venv locales en mode développement, autrement celles du docker compose.
if os.environ.get('FLASK_ENV', 'DEVELOPMENT') == 'DEVELOPMENT': load_dotenv()

def setup():
    '''
        Initialize les bases de données et leurs schémas.
    '''
    
    with Database() as db:
        print(Fore.YELLOW + "Création de la base de données pour AKSM.")

        # Modèles (oui, il est possible d'importer des packages ailleurs dans le code).
        from .aksm.device import Device
        from .aksm.history import History

        # Ajouter d'autres imports de schémas ici si nécessaire.
        # ...
        
        # Créé la base de données (on pourrait avoir un fichier avec une liste de db à créer).
        db.create_database(os.environ.get('MYSQL_DATABASE'))

        # On se positionne sur la base.
        db.execute(f"USE {os.environ.get('MYSQL_DATABASE')}")
        
        print(Fore.YELLOW + "Préparation du schéma sql.")
        
        # Créé les tables.
        db.execute(Device.model)
        db.execute(History.model)

        # Ajoutez ici d'autres exécutions de schéma si nécessaire.
        # ...

        print(Fore.LIGHTGREEN_EX + "Exécution du schéma terminé.")