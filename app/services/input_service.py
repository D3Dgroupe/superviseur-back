# app/services/input_service.py
from datetime import datetime
from zoneinfo import ZoneInfo
from app.utils.influx import write, purge_months, purge_days
from app.utils import dateutils

class InputService():
    '''
        Service de gestion des inputs.
        Ajout et suppression de points séparés en deux services.
        Ce service ne fait appel à aucun dao dans cette version.
    '''
    def __init__(self):
        print("Service d'inputs initialisé.")

    def ajouter_donnees_mois(data: dict):
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
                    'time': datetime(year, month, day).strftime("%Y-%m-%dT00:00:00Z"),
                    'value': (value / nb_jours)
                } for day in range(1, nb_jours)]

            # Option Identique.
            if data['option'] == 1:
                # Ajout des mesures pour chaque jour du mois via une liste de compréhension (plus rapide).
                measurements += [{
                    'time': datetime(year, month, day).strftime("%Y-%m-%dT00:00:00Z"),
                    'value': value
                } for day in range(1, nb_jours)]
            
            # Option Premier du mois.
            if data['option'] == 2:
                # Construction de la mesure et de sa valeur au premier du mois.
                formatted_datetime = datetime(year, month, 1).strftime("%Y-%m-%dT00:00:00Z")
            
            # Option Dernier du mois.
            if data['option'] == 3:
                # Construction de la mesure et de sa valeur à la fin du mois.
                last_day = dateutils.dernier_jour_du_mois(month, year)
                formatted_datetime = last_day.strftime("%Y-%m-%dT00:00:00Z")
            
            # Utilisé pour la purge.
            last_day = dateutils.dernier_jour_du_mois(month, year)
            mois_a_clean.append({'start': datetime(year, month, 1).strftime("%Y-%m-%dT00:00:00Z"), 'end': last_day.strftime("%Y-%m-%dT00:00:00Z")})
            
            # Ajout des mesures pour les options 2 et 3 (car soit le premier ou dernier du mois).
            if data['option'] > 1: measurements.append({ 'time': formatted_datetime, 'value': value })
        
        # Si on souhaite purger les mesures au mois.
        if data['mode'] == 1: purge_months(mois_a_clean, data['capteur'])

        # Envoi les données vers influx db (peut prendre un certain temps).
        write(data['capteur'], measurements, pool = 1000)

        return measurements

    def ajouter_donnees_jour(data: dict):
        # Les valeurs formattées.
        measurements = []
        days_a_clean = []
        
        for item in data['datablocs']:
            # Non bloquant si la clé n'existe pas.
            date, value = item.get("date"), item.get("value")

            # Si l'un des trois paramètres n'est pas renseigné.
            if None in (date, value): continue

            paris_timezone = ZoneInfo("Europe/Paris")
            local_datetime = datetime.strptime(f'{date}', "%Y-%m-%d").replace(tzinfo = paris_timezone)

            # Début de journée sinon fin de journée.
            datetime_str = local_datetime.strftime("%Y-%m-%dT00:00:00Z" if data['option'] == 0 else "%Y-%m-%dT23:59:00Z")

            # Ajoute dans les mesures une nouvelle entrée.
            days_a_clean.append({'start': local_datetime.strftime("%Y-%m-%dT00:00:00Z"), 'end': local_datetime.strftime("%Y-%m-%dT23:59:00Z")})
            
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
    
    def ajouter_donnees_heure(data: dict):
        # Les valeurs formattées.
        measurements = []
        
        for item in data['datablocs']:
            # Non bloquant si la clé n'existe pas.
            date, time, value = item.get("date"), item.get("time"), item.get("value")

            # Si l'un des trois paramètres n'est pas renseigné.
            if None in (date, time, value): continue

            paris_timezone = ZoneInfo("Europe/Paris")
            local_datetime = datetime.strptime(f'{time} {date}', "%H:%M %Y-%m-%d").replace(tzinfo = paris_timezone)

            datetime_str = local_datetime.strftime("%Y-%m-%dT%H:%M:00Z")
            
            # Ajoute dans les mesures une nouvelle entrée.
            measurements.append({ 'time': datetime_str, 'value': value })
        
        # On préfère ne pas altérer le dictionnaire original.
        new_data = dict(data)
        new_data.update({'measurements': measurements})

        # Envoi les données vers influx db (peut prendre un certain temps).
        write(data['capteur'], measurements, pool = 1000)

        return new_data