'''
    Pour AKSM Février 2024
'''

import colorama
import pandas as pd
from zoneinfo import ZoneInfo
from datetime import datetime
from colorama import Fore
import os
import json
import re
import hashlib
import time

import pytz

# Initialize colorama.
colorama.init(autoreset = True)

def convert(file_path: str, save = False, separator: str = ','):
    # Affiche un petit message d'information.
    print(Fore.YELLOW + "Conversion vers le format JSON en cours veuillez patienter...")

    # Timer start.
    start_time = time.time()
    
    # Définition du TimeZone (TODO : on pourrait le mettre dans une variable d'env ça serait plus propre)  # La fusée horaire (le fuseau pardon).
    cet_timezone = pytz.timezone('Europe/Paris')
       
    # Charge le fichier csv et ignore les headers, on utilise le séparateur point virgule.
    try: csv_data = pd.read_csv(file_path, na_values = [''], skiprows = [0], header = None, sep = separator)
    except: print(Fore.RED + f"ERROR : La fichier CSV n'est pas valide."); return None
    
    # Le nom des instruments.
    instruments = csv_data.iloc[0, 1:].values

    # Unités à parir de la ligne 3 (on compte à partir de zéro) et deuxième entrée (toujours à partir de zéro).
    units = csv_data.iloc[1, 1:].values
    
    # Données qui déterminent si le capteur est digital ou analogue.
    digital_analog = csv_data.iloc[2, 1:].values
    
    # Fréquence des mesures.
    sample_rates = csv_data.iloc[3, 1:].values

    # Total du nombre de missing.
    total_missing = 0

    # Début et fin des relevés.
    start = None; end = None

    data = {}
    
    for i in range(4, len(csv_data)):
        
        # Toutes les valeurs à partir de la quatrième ligne (y compris le datetime à l'indice zéro).
        row = csv_data.iloc[i, :].values
        
        # On sait que la première valeur est notre timestamp qu'on met au propre en le formattant et le transformant en ts conscient de son fuseau.
        local_time_str = re.sub(' +', ' ', row[0]).strip()

        try: 
            local_datetime = cet_timezone.localize(datetime.strptime(local_time_str, "%H:%M:%S %d/%m/%Y"),is_dst=None)
        except: 
            try: local_datetime = cet_timezone.localize(datetime.strptime(local_time_str, "%H:%M:%S %d/%m/%Y"),is_dst=None)
            except: return None
        #Ancien code (pas sûr qu'il fonctionnait mais je crois pas car sur l'import PC GTB ça n'a pas fonctionné)  
        #try:
        #    local_datetime = datetime.strptime(local_time_str, "%H:%M:%S %d/%m/%Y").replace(tzinfo = paris_timezone)
        #except:
        #    try: local_datetime = datetime.strptime(local_time_str, "%H:%M:%S %m/%d/%Y").replace(tzinfo = paris_timezone)
        #    except: return None
        
        # Les mesures après la première valeur.
        measurements = row[1:]

        for j, instrument in enumerate(instruments):
            # Instrument doit exister.
            if pd.isna(instrument): continue
            
            # Le nom a des espaces blancs en trop on va arranger ça proprement.
            try: instrument = re.sub(' +', ' ', str(instrument)).upper()
            except: continue

            # Nous donne un identifiant unique utile pour notre dictionnaire et éviter les doublons.
            id = hashlib.sha256(instrument.encode()).hexdigest()

            # Capture le hash tag.
            tag = re.search(r'#(.*)', instrument).group(1)

            # Capture le nom (sans le hash tag).
            nom = re.search(r'(.*?)(?=\s*#)', instrument).group(1)

            # Servira pour notre champ date « parent » désormais séparé des heures.
            date_str = local_datetime.strftime("%Y-%m-%d")

            try:
                # On vérifie si on a un entier pour représenter vrai ou faux.
                digital = int(digital_analog[j])
            except:
                # Autrement on essaye de tester si on peut obtenir true ou false (valeur littérale du booléen).
                try: digital = (1 if str.lower(digital_analog[j]) == 'true' else 0)
                except: digital = None

            # On tente d'extraire la fréquence et seulement la fréquence (1Min → 1) grâce à une regex.
            try: frequence = float(re.sub(r"^[^\d]*(\d+).*", r"\1", str(sample_rates[j])))
            except: frequence = None

            # Ajoute cette entrée au dictionnaire si elle n'existe pas encore.
            if id not in data:
                data[id] = {
                    "hash": id,
                    "tag": tag,
                    "nameGtc": nom,
                    "missingno": 0,
                    "date": date_str,
                    "measurements": [],
                    "unit": units[j] if not pd.isna(units[j]) else None,
                    "digital": digital,
                    "rate": frequence if not pd.isna(sample_rates[j]) else None
                }

            # Permet de spécifier que la valeur est manquante ou non.
            manquante = False

            # Attention il faut tenter de cast, si le cast echoue on considère la valeur manquante.
            try: float(measurements[j])
            except: data[id]["missingno"] += 1; manquante = True; total_missing += 1
            
            # Nouvelle entrée (les valeurs sont remplacées par None si elles n'existent pas dans le csv).
            measurement_entry = {
                # Ancien code à supprimer si fonctionnel "time": local_datetime.astimezone(ZoneInfo("UTC")).isoformat().replace('+00:00', 'Z'),
                "time": local_datetime.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "value": float(measurements[j]) if not manquante else None
            }

            # Défini le début et fin des mesures lorsque cela est possible (pour garder à la sortie une trace dans MySQL).
            if start == None: local_datetime or None
            if j == len(instruments): end = local_datetime

            data[id]["measurements"].append(measurement_entry)

    # Transforme les valeurs sous forme de liste.
    output = list(data.values())

    # Sauve le json sur le disque si nécessaire (on sépare le fichier de son chemin et on extrait uniquement le nom avec [0]).
    if (save == True): save_json(json.dumps(output, indent = 4), "app/temp", os.path.splitext(os.path.basename(file_path))[0])

    end_time = time.time()
    print(Fore.LIGHTMAGENTA_EX + f"Temps de création du dictionnaire d'environ {round(end_time - start_time, 2)} secondes.")
    
    # Sérialisation vers un objet json formatté.
    return {'start': start, 'end': end, 'missing': total_missing, 'equipements': output}

def save_json(json_data, folder, file):
    # On s'assure que le répertoire existe (os.path.join permet une compatibilité cross-platform).
    directory = os.path.join(folder)
    os.makedirs(directory, exist_ok = True)
    
    # On sauvegarde le fichier.
    with open(os.path.join(folder, f"{file}.json"), 'w') as file:
        file.write(json_data)

