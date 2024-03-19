# main.py
import os
from threading import Thread
from colorama import Fore

from app import create_app
from app.services import device_service as ds
from app.utils.file_watcher import start_watching
from app.utils.ping import run_periodic_pings
from app.utils.csv_to_json import convert
from app.utils.influx import transmute

# Création de l'application web.
app = create_app()

# La fonction (callback) déclenchée par le watch dog (reste à compléter la logique).
def on_new_file_created(file_path):
    print(Fore.YELLOW + f"Un nouveau csv vient de pop dans le dossier à l'adresse : {file_path}.")

    # Appelle la procédure afin de convertir le csv en json (dictionnaire).
    data = convert(file_path)

    # Les équipements dont on va pull les infos depuis MySQL.
    equipments = []

    # On parcours les équipements du csv et on vérifie leur présence dans la base de données pour en extraire les infos.
    for eq in data['equipements']:
        # Récupère les informations au complet de l'appareil.
        eq_full = ds.recuperer_appareil_par_nom(eq['tag'])
        
        # On ne mettra pas à jour le dictionnaire si le tag du csv n'existe pas en base de données.
        if eq_full is None: continue

        # Met à jour le dictionnaire.
        eq.update({"tag": eq_full['tag']})
        eq.update({"nameGtc": eq_full['nameGtc']})
        eq.update({"nameDisplayed": eq_full['nameDisplayed']})
        eq.update({"threshold": eq_full['threshold']})

        # Les groupes.
        eq.update({"deviceGroup": eq_full['deviceGroup']})

        # Push ce dictionnaire dans la liste.
        equipments.append(eq)

    # Passe les données du json vers influxdb dans le bucket spécifié en variable d'environnement.
    transmute(equipments, pool = 16_000)

    print(Fore.LIGHTGREEN_EX + "Les données ont été transféré vers InfluxDB.")

if __name__ == '__main__':
    # Créer les répertoires critiques de fonctionnement s'ils n'existent pas.
    if not os.path.exists(app.config['CSV_FOLDER_PATH']): os.makedirs(app.config['CSV_FOLDER_PATH'])
    if not os.path.exists(app.config['UPLOADS_PATH']): os.makedirs(app.config['UPLOADS_PATH'])

    # Lance deux threads pour surveiller les répertoires et émettre une alerte lorsqu'un service critique est injoignable.
    watcher_thread = Thread(target = start_watching, args = (app.config['CSV_FOLDER_PATH'], on_new_file_created, app.config['WATCHDOG_SLEEP_INTERVAL']), daemon = True)
    ping_thread = Thread(target = run_periodic_pings, args = (3600, app.config['FLASK_ENV']), daemon = True)
    
    # Démarre les threads.
    watcher_thread.start()
    ping_thread.start()
    
    # Lance l'application et évite qu'un nouveau thread ne soit exécuté en cas de rechargement à chaud (hot reload) lorsque le debugger est actif.
    # Attention : Bloquant (ne rien exécuter après cette ligne).
    app.run(debug = app.config['DEBUG'], use_reloader = False)