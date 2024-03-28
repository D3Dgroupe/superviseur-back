# app/services/purge_service.py
from datetime import datetime
from zoneinfo import ZoneInfo
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

            # Conversion des fuseaux (rend l'objet utc non-naïf).
            paris_timezone = ZoneInfo("Europe/Paris")
            local_datetime = datetime.strptime(f'{date}', "%Y-%m-%d").replace(tzinfo = paris_timezone)

            # Ajoute dans les mesures une nouvelle entrée.
            days.append({'start': local_datetime.strftime("%Y-%m-%dT00:00:00Z"), 'end': local_datetime.strftime("%Y-%m-%dT23:59:00Z")})

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

            months.append({'start': datetime(year, month, 1).strftime("%Y-%m-%dT00:00:00Z"), 'end': last_day.strftime("%Y-%m-%dT00:00:00Z")})
        
        # On préfère ne pas altérer le dictionnaire original.
        new_data = dict(data)
        new_data.update({'months': months})

        # On souhaite purger les mesures au mois.
        return purge_months(months, data['capteur'])