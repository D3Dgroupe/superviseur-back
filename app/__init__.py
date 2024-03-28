# app/__init__.py
import colorama
import os
from threading import Thread
from colorama import Fore
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from app.models import setup
from app.routes import register_routes
from app.config.application import DevelopmentConfig, ProductionConfig
from app.services import device_service as ds
from app.utils.csv_to_json import convert
from app.utils.influx import transmute
from app.utils.file_watcher import start_watching_linux, start_watching_windows
from app.utils.ping import run_periodic_pings

# On appelle load_dotenv() pour les venv locales en mode développement, autrement celles du docker compose.
if os.environ.get('FLASK_ENV', 'DEVELOPMENT') == 'DEVELOPMENT': load_dotenv()

# Initialize colorama (=~ méthode statique).
colorama.init(autoreset = True)

# La fonction (callback) déclenchée par le watch dog (reste à compléter la logique).
def on_new_file_created(file_path):

    print(Fore.YELLOW + f"Un nouveau csv vient de pop dans le dossier à l'adresse : {file_path}.")

    if file_path is None: return

    # Vérifie s'il s'agit bien d'un fichier csv [1] correspond à l'extension (0 étant le nom) et [1:] afin de ne pas inclure le dot.
    if str(os.path.splitext(file_path)[1][1:]).upper() != 'CSV': return

    print(Fore.YELLOW + f"Le fichier est valide, on va tenter de l'importer.")

    # Appelle la procédure afin de convertir le csv en json (dictionnaire).
    data = convert(file_path)

    # Les équipements dont on va pull les infos depuis MySQL.
    equipments = []

    # On parcours les équipements du csv et on vérifie leur présence dans la base de données pour en extraire les infos.
    for eq in data['equipements']:
        # Récupère les informations au complet de l'appareil.
        eq_full = ds.recuperer_appareil_par_tag(eq['tag'])
        
        # On ne mettra pas à jour le dictionnaire si le tag du csv n'existe pas en base de données.
        if eq_full is None: continue

        # Met à jour le dictionnaire.
        eq.update({"tag": eq_full['tag']})
        eq.update({"nameGtc": eq_full['nameGtc']})
        eq.update({"nameDisplayed": eq_full['nameDisplayed']})
        eq.update({"unit": eq_full['unit']})
        eq.update({"previsionnel": eq_full['previsionnel']})
        eq.update({"threshold": eq_full['threshold']})

        # Les groupes.
        eq.update({"deviceGroup": eq_full['deviceGroup']})

        # Push ce dictionnaire dans la liste.
        equipments.append(eq)

    # On ne continue pas si aucun équipement n'a pu être traité depuis le csv (car pas les bons tags par exemple).
    if len(equipments) == 0: return
    
    # Passe les données du json vers influxdb dans le bucket spécifié en variable d'environnement.
    transmute(equipments, pool = 16_000)

    print(Fore.LIGHTGREEN_EX + "Les données ont été transféré vers InfluxDB.")

def create_app():
    '''
        Point de démarrage en mode production (c'est le script qui gère).
    '''
    app = Flask(__name__)
    
    # Nécessaire pour la gestion du partage de ressources d'origine croisée (ex : communication du front vers le back).
    CORS(app)

    # Récupère la configuration de développement ou de production selon l'environnement (FLASK_ENV) spécifié.
    if os.environ.get('FLASK_ENV').upper() == 'PRODUCTION': app.config.from_object(ProductionConfig)
    else: app.config.from_object(DevelopmentConfig)

    # Le répertoire à surveiller, la fonction callback et l'interval entre chaque heart beat.
    args_surveillance = (app.config['LISTEN_FOLDER_PATH'], on_new_file_created, app.config['WATCHDOG_SLEEP_INTERVAL'])

    # Créer les répertoires critiques de fonctionnement s'ils n'existent pas.
    if not os.path.exists(app.config['LISTEN_FOLDER_PATH']): os.makedirs(app.config['LISTEN_FOLDER_PATH'])
    if not os.path.exists(app.config['UPLOADS_PATH']): os.makedirs(app.config['UPLOADS_PATH'])

    print(Fore.YELLOW + "Lancement des Threads.")

    # Création de deux threads (daemon non bloquant lors de la fermeture).
    watcher_thread = Thread(target = (start_watching_windows if os.environ.get('HOST_OS') == 'WINDOWS' else start_watching_linux), args = args_surveillance, daemon = True)
    ping_thread = Thread(target = run_periodic_pings, args = (3600, app.config['FLASK_ENV']), daemon = True)
    
    # Démarre les threads.
    watcher_thread.start()
    ping_thread.start()

    # Création des schéma sql.
    setup()
    
    # Importation des routes.
    register_routes(app)

    # Import intercepteur d'erreur (404).
    from .exceptions.errors import not_found_error, internal_error
    app.errorhandler(404)(not_found_error)
    app.errorhandler(500)(internal_error)

    # Enregistrer d'autres intercepteurs ici.
    # ...
    
    return app