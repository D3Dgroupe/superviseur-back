# config.py
import os
from dotenv import load_dotenv

# On appelle load_dotenv() pour les venv locales en mode développement, autrement celles du docker compose.
if os.environ.get('FLASK_ENV', 'DEVELOPMENT') == 'DEVELOPMENT': load_dotenv()

class Config:
    WATCHDOG_SLEEP_INTERVAL = 10
    UPLOADS_PATH = 'app/uploads'

class DevelopmentConfig(Config):
    # Par héritage, les variables WATCHDOG_SLEEP_INTERVAL et UPLOADS_PATH sont également comprises.
    FLASK_ENV = 'DEVELOPMENT'
    DEBUG = True
    
    # Si dans le fichier d'environnement (.env) la variable `CSV_FOLDER_PATH` n'existe pas alors on prend `app/storage` par défaut.
    CSV_FOLDER_PATH = 'app/storage'

class ProductionConfig(Config):
    # Par héritage, les variables WATCHDOG_SLEEP_INTERVAL et UPLOADS_PATH sont également comprises.
    FLASK_ENV = 'PRODUCTION'
    DEBUG = False
    
    # Si la variable d'environnement `LISTEN_FOLDER_PATH` n'existe pas, utilise celle par défaut.
    CSV_FOLDER_PATH = os.environ.get('LISTEN_FOLDER_PATH')