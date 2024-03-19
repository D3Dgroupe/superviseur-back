# app/routes/inputs.py
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from zoneinfo import ZoneInfo
from app.utils.influx import purge, purge_days, purge_months
from app.utils import dateutils

suppression_bp = Blueprint('suppression', __name__, url_prefix = '/suppression')

@suppression_bp.route('<string:tag>/purge', methods = ['DELETE'])
@cross_origin()
def purger_mesure(tag: str):
    # Purge toutes les mesures de cet équipement.
    purge(tag)

    # Renvoie un corps vide et un statut succès (200).
    return jsonify('Les points ont été supprimés.'), 200

@suppression_bp.route('/jour', methods = ['POST'])
@cross_origin()
def purger_mesure_jour():
    # Contient le corps de la requête.
    data = request.get_json()

    # Les valeurs formattées.
    days = []
    
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
    purge_days(days, data['device'])

    # Renvoie le dictionnaire original et un statut succès (200).
    return jsonify('Les points ont été supprimés.'), 200

@suppression_bp.route('/mois', methods = ['POST'])
@cross_origin()
def purger_mesure_mois():
    # Les données reçues à formatter.
    data = request.get_json()

    # Les valeurs formattées.
    months = []

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
    purge_months(months, data['device'])

    # Retourne le nouveau dictionnaire et le statut code (OK).
    return jsonify('Les points ont été supprimés.'), 200