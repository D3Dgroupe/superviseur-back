import time
import os
from dotenv import load_dotenv
import pytz

from datetime import datetime
from dateutil.relativedelta import relativedelta
from colorama import Fore

from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS

# On appelle load_dotenv() pour les venv locales en mode développement, autrement celles du docker compose.
if os.environ.get('FLASK_ENV', 'DEVELOPMENT') == 'DEVELOPMENT': load_dotenv()

# Données de configuration d'influx DB (voir docker-compose.yml).
url = os.environ.get('INFLUXDB_HOST')
token = os.environ.get('INFLUXDB_TOKEN')
org = os.environ.get('INFLUXDB_ORG')
bucket = os.environ.get('INFLUXDB_BUCKET')

def transmute(data: dict, pool: int, test = False):
    '''
        On doit convertir les données json en line protocol pour les rendre compatibles avec influx db.
        Documentation :
        https://www.influxdata.com/blog/import-json-data-influxdb-using-python-go-javascript-client-libraries/
    '''

    print(Fore.LIGHTYELLOW_EX + "Importation vers InfluxDB en cours...")

    # Initialisation du client InfluxDB.
    client = InfluxDBClient(url = url, token = token, org = org)
    
    # Timer start.
    start_time = time.time()
    total = 0

    with client.write_api(write_options = WriteOptions(batch_size = pool)) as write_api:
        # Pour chaque enregistrement.
        for record in data:
            # Compteur de points.
            counter = 0
            
            # Ces données sont fixes et ne changent pas pour un équipement.
            device = record["nameGtc"]
            tag = record["tag"]
            name_displayed = record["nameDisplayed"]
            threshold = record["threshold"]
            unit = record["unit"]
            previsionnel = record["previsionnel"]

            # Groupes d'appartenance.
            group_a = record["deviceGroup"]
            
            # Pour chaque mesure d'un équipement.
            for measurement in record["measurements"]:
                
                # Création du point.
                point = Point(tag)

                # Les groupes d'appartenance.
                point.tag("ga", group_a)

                point.tag("name_displayed", name_displayed)
                point.tag("name_gtc", device)
                point.tag("previsionnel", previsionnel)

                # Le seuil si applicable.
                if threshold is not None: point.field("threshold", threshold)
                
                # Notre utilisé de mesure (peuvent être différents types de données).
                point.field(unit, measurement["value"])
                
                # Le point dans le temps.
                point.time(measurement["time"])
                
                if not test: write_api.write(bucket = bucket, org = org, record = point)
                counter = counter + 1

            # Pour déboggage.
            # datetime_obj = pd.to_datetime(measurement["time"])
            # formatted_datetime = datetime_obj.strftime("%d/%m/%Y %H:%M:%S")

            total = total + counter
            print(Fore.LIGHTGREEN_EX + f"Ajout de {counter} mesures pour l'équipement {device}.")
        
        end_time = time.time()
        print(Fore.GREEN + f"{total} nouveaux points ont été ajoutés au bucket.")
        print(Fore.LIGHTMAGENTA_EX + f"Temps de traitement du dictionnaire vers influx environ {round(end_time - start_time, 2)} secondes.")

def write(device: dict, points: dict, pool: int):
    '''
        Ecrit des valeurs manuelles.
    '''

    # Initialisation du client InfluxDB.
    client = InfluxDBClient(url = url, token = token, org = org)
    
    # Timer start.
    start_time = time.time()

    with client.write_api(write_options = WriteOptions(batch_size = pool)) as write_api:
        # Compteur de points.
        counter = 0

        # Pour chaque enregistrement.
        for data in points:
            
            # Création du point.
            point = Point(device['tag'])

            # Les groupes d'appartenance.
            point.tag("ga", device['deviceGroup'])

            point.tag("name_displayed", device['nameDisplayed'])
            point.tag("name_gtc", device['nameGtc'])
            point.tag("previsionnel", device['previsionnel'])

            # Le seuil si applicable.
            if device['threshold'] is not None: point.field("threshold", device['threshold'])
            
            # Notre utilisé de mesure (peuvent être différents types de données).
            point.field(device['unit'], data["value"])
            
            # Le point dans le temps.
            point.time(data["time"])
                
            write_api.write(bucket = bucket, org = org, record = point)
            counter = counter + 1
        
        end_time = time.time()
        print(Fore.GREEN + f"{counter} nouveaux points ont été ajoutés au bucket.")
        print(Fore.LIGHTMAGENTA_EX + f"Temps de traitement du dictionnaire vers influx environ {round(end_time - start_time, 2)} secondes.")

def purge(tag: str):
    # Initialisation du client InfluxDB.
    client = InfluxDBClient(url = url, token = token, org = org)
    delete_api = client.delete_api()

    now = datetime.now()
    ten_years_ago = now - relativedelta(years = 10)
    
    # Conversion en UTC.
    start = ten_years_ago.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stop = now.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try: delete_api.delete(start = start, stop = stop, predicate = f'_measurement="{tag}"', bucket = bucket, org = org)
    except: print(Fore.RED + f"La suppression des mesures du capteur avec pour tag {tag} n'a pu avoir lieu sur le bucket {bucket}."); return False

    return True

def purge_days(days: list, device: dict):
    # Initialisation du client InfluxDB.
    client = InfluxDBClient(url = url, token = token, org = org)
    delete_api = client.delete_api()
    
    # Supprime les mesures de chaque jour spécifié.
    for day in days:
        # Points de départ et de fin des mesures à supprimer.
        start = datetime.fromisoformat(day['start'].rstrip('Z'))
        stop = datetime.fromisoformat(day['end'].rstrip('Z'))

        # Le tag de l'appareil.
        tag = device['tag']

        try: delete_api.delete(start = start, stop = stop, predicate = f'_measurement="{tag}"', bucket = bucket, org = org)
        except: print(Fore.RED + f"La suppression au jour des mesures du capteur avec pour tag {tag} n'a pu avoir lieu sur le bucket {bucket}."); return False

    return True

def purge_months(months: list, device: dict):
    # Initialisation du client InfluxDB.
    client = InfluxDBClient(url = url, token = token, org = org)
    delete_api = client.delete_api()
    
    # Supprime les mesures de chaque jour spécifié.
    for month in months:
        # Points de départ et de fin des mesures à supprimer.
        start = datetime.fromisoformat(month['start'].rstrip('Z'))
        stop = datetime.fromisoformat(month['end'].rstrip('Z'))

        # Le tag de l'appareil.
        tag = device['tag']

        try: delete_api.delete(start = start, stop = stop, predicate = f'_measurement="{tag}"', bucket = bucket, org = org)
        except: print(Fore.RED + f"La suppression au mois des mesures du capteur avec pour tag {tag} n'a pu avoir lieu sur le bucket {bucket}."); return False

    return True
