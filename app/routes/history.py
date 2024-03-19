# app/routes/history.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.historique_service import recuperer_historique_fichiers, sauvegarder_trace

'''
    Demande de la liste des fichiers importés.
    Permet de modifier le commentaire d'un import.
'''

history_bp = Blueprint('history', __name__, url_prefix = '/history')

@history_bp.route('/', methods = ['GET'])
@cross_origin()
def get_imports_list():
    # Appelle le service pour renvoyer l'historique des imports.
    data = recuperer_historique_fichiers()

    # Renvoie un code 204 en cas d'absence de données.
    if not data: return '', 204

    return jsonify(data), 200

@history_bp.route('/save/<int:id>', methods = ['POST'])
@cross_origin()
def save_import_comment(id):
    fichier = request.get_json()

    # On doit s'assurer qu'il y a bien quelque chose dans le corps de la requête (comme le nom).
    if not fichier or 'comment' not in fichier: return jsonify(fichier), 304

    sauvegarder_trace(id, fichier['comment'])

    return jsonify(fichier), 200