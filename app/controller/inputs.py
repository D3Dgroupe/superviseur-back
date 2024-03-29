# app/controller/inputs.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.input_service import InputService

inputs_bp = Blueprint('inputs', __name__, url_prefix = '/inputs')
service = InputService()

@inputs_bp.route('/mois', methods = ['POST'])
@cross_origin()
def ajout_donnees_mois():
    # Les données reçues à formatter.
    data = request.get_json()

    measurements = service.ajouter_donnees_mois(data)

    if len(measurements) == 0: jsonify("Aucun point n'a pu être ajouté vers Influx."), 400

    # Renvoie les valeurs ajoutés au front.
    return jsonify(measurements), 200

@inputs_bp.route('/heure', methods = ['POST'])
@cross_origin()
def ajout_donnees_heure():
    # Les données reçues à formatter.
    data = request.get_json()

    measurements = service.ajouter_donnees_heure(data)

    # Retourne le nouveau dictionnaire et le statut code (OK).
    return jsonify(measurements), 200

@inputs_bp.route('/jour', methods = ['POST'])
@cross_origin()
def ajout_donnees_jour():
    # Les données reçues à formatter.
    data = request.get_json()

    measurements = service.ajouter_donnees_jour(data)

    # Retourne le nouveau dictionnaire et le statut code (OK).
    return jsonify(measurements), 200
