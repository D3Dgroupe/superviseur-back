# app/services/purge_service.py
from datetime import datetime
from zoneinfo import ZoneInfo

import pytz
from app.utils.influx import purge, purge_days, purge_months
from app.utils import dateutils

class PurgeService():
    '''
        Service de gestion des inputs à purger.
        Ajout et suppression de points séparés en deux services.
        Ce service ne fait appel à aucun dao dans cette version.
    '''
    def __init__(self):
        print("Initialisation de `Purge` Service.")

    def purge_all_by_tag(self, tag: str):
        return purge(tag)
    
    def purge_days(self, data: dict):
        # Les valeurs formattées.
        days = []

        # Traitement des données pour compatibilité Influx.
        for item in data['datablocs']:
            # Vérifie que la clé existe.
            date = item.get("date")

            # La date doit être spécifiée pour créer un interval.
            if date == None: continue

            # On converti la date récupérée en format Datetime pour pouvoir la réutiliser après
            variable_date = datetime.strptime(date, "%Y-%m-%d")
            # Début de journée et fin de journée.
            datetime_str_debut = variable_date.replace(hour = 00, minute = 00, second = 00).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            datetime_str_fin = variable_date.replace(hour = 23, minute = 59, second = 59).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            # Ajoute dans les mesures une nouvelle entrée.
            days.append({'start': datetime_str_debut, 'end': datetime_str_fin})

        # On préfère ne pas altérer le dictionnaire original.
        new_data = dict(data)
        new_data.update({'days': days})

        # On souhaite purger les mesures au jour.
        return purge_days(days, data['capteur'])

    def purge_months(self, data: dict):
        # Les valeurs formattées.
        months = []

        # Traitement des données pour compatibilité Influx.
        for item in data['datablocs']:
            # Non bloquant si la clé n'existe pas.
            month, year, = item.get("month"), item.get("year")

            # Si l'un des deux paramètres n'est pas renseigné.
            if None in (month, year): continue

            # Passe par une fonction utilitaire pour le nombre de jours dans le mois de l'année spécifiée.
            last_day = dateutils.dernier_jour_du_mois(month, year)
            last_day_utc = last_day.replace(hour = 23, minute = 59, second = 59).astimezone(pytz.utc)
            formatted_datetime_last_day = last_day_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            formatted_datetime_first_day = datetime(year, month, 1).replace(hour = 00, minute = 00, second = 00).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            months.append({'start': formatted_datetime_first_day, 'end': formatted_datetime_last_day})
        
        # On préfère ne pas altérer le dictionnaire original.
        new_data = dict(data)
        new_data.update({'months': months})

        # On souhaite purger les mesures au mois.
        return purge_months(months, data['capteur'])