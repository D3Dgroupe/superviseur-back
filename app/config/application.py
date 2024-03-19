# config.py
import os

class Config:
    WATCHDOG_SLEEP_INTERVAL = 10
    UPLOADS_PATH = 'app/uploads'

class DevelopmentConfig(Config):
    FLASK_ENV = 'DEVELOPMENT'
    DEBUG = True
    
    # Si dans le fichier d'environnement (.env) la variable `CSV_FOLDER_PATH` n'existe pas alors on prend `app/storage` par défaut.
    CSV_FOLDER_PATH = 'app/storage'

class ProductionConfig(Config):
    FLASK_ENV = 'PRODUCTION'
    DEBUG = False
    CSV_FOLDER_PATH = os.getenv('LISTEN_FOLDER_PATH', 'app/storage')