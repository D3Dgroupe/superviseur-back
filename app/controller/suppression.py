# app/controller/suppression.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.purge_service import PurgeService

suppression_bp = Blueprint('suppression', __name__, url_prefix = '/suppression')
service = PurgeService()

@suppression_bp.route('<string:tag>/purge', methods = ['DELETE'])
@cross_origin()
def purger_mesure(tag: str):
    # Purge toutes les mesures de cet équipement.
    deleted = service.purge_all_by_tag(tag)

    # Renvoie un corps vide et un statut succès (200).
    if deleted: return jsonify('Tous les points de la mesure ont été supprimés.'), 200
    else: return jsonify('Une erreur est survenue lors de la suppression des points.'), 400

@suppression_bp.route('/jour', methods = ['POST'])
@cross_origin()
def purger_mesure_jour():
    # Contient le corps de la requête.
    data = request.get_json()

    deleted = service.purge_days(data)

    # Renvoie le dictionnaire original et un statut succès (200).
    if deleted: return jsonify('Les points ont été supprimés.'), 200
    else: return jsonify('Une erreur est survenue lors de la suppression des points.'), 400

@suppression_bp.route('/mois', methods = ['POST'])
@cross_origin()
def purger_mesure_mois():
    # Les données reçues à formatter.
    data = request.get_json()

    deleted = service.purge_months(data)

    # Retourne le nouveau dictionnaire et le statut code (OK).
    if deleted: return jsonify('Les points ont été supprimés.'), 200
    else: return jsonify('Une erreur est survenue lors de la suppression des points.'), 400