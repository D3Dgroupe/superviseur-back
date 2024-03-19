# app/__init__.py
import colorama
import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from app.models import setup
from app.config.application import DevelopmentConfig, ProductionConfig

# On appelle load_dotenv() pour les venv locales en mode développement, autrement celles du docker compose.
if os.environ.get('FLASK_ENV', 'DEVELOPMENT') == 'DEVELOPMENT': load_dotenv()

# Initialize colorama (=~ méthode statique).
colorama.init(autoreset = True)

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Récupère la configuration de développement ou de production selon l'environnement (FLASK_ENV) spécifié.
    if os.environ.get('FLASK_ENV') == 'PRODUCTION': app.config.from_object(ProductionConfig)
    else: app.config.from_object(DevelopmentConfig)

    # Création des schéma sql.
    setup()
    
    # Importation des routes.
    from .routes.history import history_bp
    from .routes.importation import importation_bp
    from .routes.devices import devices_bp
    from .routes.inputs import inputs_bp
    from .routes.suppression import suppression_bp

    # Importer d'autres routes ici.
    # ...
    
    # Enregistre les routes spécifiques au serveur.
    app.register_blueprint(history_bp)
    app.register_blueprint(importation_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(inputs_bp)
    app.register_blueprint(suppression_bp)

    # Enregistrer d'autres routes ici.
    # ...

    # Import intercepteur d'erreur (404).
    from .exceptions.errors import not_found_error, internal_error
    app.errorhandler(404)(not_found_error)
    app.errorhandler(500)(internal_error)

    # Enregistrer d'autres intercepteurs ici.
    # ...
    
    return app