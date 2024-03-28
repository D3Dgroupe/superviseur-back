# app/services/input_service.py
from datetime import datetime
import pytz
from app.utils.influx import write, purge_months, purge_days
from app.utils import dateutils

class InputService():
    '''
        Service de gestion des inputs.
        Ajout et suppression de points séparés en deux services.
        Ce service ne fait appel à aucun dao dans cette version.
    '''
    def __init__(self):
        print("Initialisation de `Input` Service.")

    def ajouter_donnees_mois(self, data: dict):
        # Les valeurs formattées.
        measurements = []
        mois_a_clean = []

        for item in data['datablocs']:
            # Non bloquant si la clé n'existe pas.
            month, year, value = item.get("month"), item.get("year"), item.get("value")

            # Si l'un des trois paramètres n'est pas renseigné.
            if None in (month, year, value): continue

            # Passe par une fonction utilitaire pour le nombre de jours dans le mois de l'année spécifiée.
            nb_jours = dateutils.dernier_jour_du_mois(month, year).day + 1

            # Option Moyenne.
            if data['option'] == 0:
                # Ajout des mesures pour chaque jour du mois via une liste de compréhension (plus rapide).
                measurements += [{
                    'time': datetime(year, month, day).replace(hour = 23, minute = 59, second = 59).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'value': (value / nb_jours)
                } for day in range(1, nb_jours)]

            # Option Identique.
            if data['option'] == 1:
                # Ajout des mesures pour chaque jour du mois via une liste de compréhension (plus rapide).
                measurements += [{
                    'time': datetime(year, month, day).replace(hour = 23, minute = 59, second = 59).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    'value': value
                } for day in range(1, nb_jours)]
            
            # Option Premier du mois.
            if data['option'] == 2:
                # Construction de la mesure et de sa valeur au premier du mois.
                formatted_datetime = datetime(year, month, 1).replace(hour = 00, minute = 00, second = 00).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            # Option Dernier du mois.
            if data['option'] == 3:
                # Construction de la mesure et de sa valeur à la fin du mois.
                # Date initiale au format timezone
                last_day = dateutils.dernier_jour_du_mois(month, year)
                last_day_utc = last_day.replace(hour = 23, minute = 59, second = 59).astimezone(pytz.utc)
                formatted_datetime = last_day_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

            # Utilisé pour la purge.
            last_day = dateutils.dernier_jour_du_mois(month, year)
            last_day_utc = last_day.replace(hour = 23, minute = 59, second = 59).astimezone(pytz.utc)
            formatted_datetime_last_day = last_day_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
            formatted_datetime_first_day = datetime(year, month, 1).replace(hour = 00, minute = 00, second = 00).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            mois_a_clean.append({'start': formatted_datetime_first_day, 'end': formatted_datetime_last_day})
            
            # Ajout des mesures pour les options 2 et 3 (car soit le premier ou dernier du mois).
            if data['option'] > 1: measurements.append({ 'time': formatted_datetime, 'value': value })
        
        # Si on souhaite purger les mesures au mois.
        if data['mode'] == 1: purge_months(mois_a_clean, data['capteur'])

        # Envoi les données vers influx db (peut prendre un certain temps).
        write(data['capteur'], measurements, pool = 1000)

        return measurements

    def ajouter_donnees_jour(self, data: dict):
        # Les valeurs formattées.
        measurements = []
        days_a_clean = []
        
        for item in data['datablocs']:
            # Non bloquant si la clé n'existe pas.
            date, value = item.get("date"), item.get("value")

            # Si l'un des trois paramètres n'est pas renseigné.
            if None in (date, value): continue

            # On converti la date récupérée en format Datetime pour pouvoir la réutiliser après
            variable_date = datetime.strptime(date, "%Y-%m-%d")
            # Début de journée sinon fin de journée.
            datetime_str_debut = variable_date.replace(hour = 00, minute = 00, second = 00).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            datetime_str_fin = variable_date.replace(hour = 23, minute = 59, second = 59).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            datetime_str = datetime_str_debut if data['option'] == 0 else datetime_str_fin

            # Ajoute dans les mesures une nouvelle entrée.
            days_a_clean.append({'start': datetime_str_debut, 'end': datetime_str_fin})
            
            # Ajoute dans les mesures une nouvelle entrée.
            measurements.append({ 'time': datetime_str, 'value': value })
        
        # On préfère ne pas altérer le dictionnaire original.
        new_data = dict(data)
        new_data.update({'measurements': measurements})

        # Si on souhaite purger les mesures au jour.
        if data['mode'] == 1: purge_days(days_a_clean, data['capteur'])

        # Envoi les données vers influx db (peut prendre un certain temps).
        write(data['capteur'], measurements, pool = 1000)

        return new_data
    
    def ajouter_donnees_heure(self, data: dict):
        # Les valeurs formattées.
        measurements = []
        
        for item in data['datablocs']:
            # Non bloquant si la clé n'existe pas.
            date, time, value = item.get("date"), item.get("time"), item.get("value")

            # Si l'un des trois paramètres n'est pas renseigné.
            if None in (date, time, value): continue
            # On converti la date récupérée en format Datetime pour pouvoir la réutiliser après
            variable_date = datetime.strptime(date, "%Y-%m-%d")
            variable_time = datetime.strptime(time, "%H:%M")
            datetime_str = variable_date.replace(hour = variable_time.hour, minute = variable_time.minute, second = 00).astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Ajoute dans les mesures une nouvelle entrée.
            measurements.append({ 'time': datetime_str, 'value': value })
        
        # On préfère ne pas altérer le dictionnaire original.
        new_data = dict(data)
        new_data.update({'measurements': measurements})

        # Envoi les données vers influx db (peut prendre un certain temps).
        write(data['capteur'], measurements, pool = 1000)

        return new_data