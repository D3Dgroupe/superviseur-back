# app/controller/imports.py
import os
import uuid
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.import_service import ImportService

imports_bp = Blueprint('imports', __name__, url_prefix = '/history')
service = ImportService()

@imports_bp.route('/', methods = ['GET'])
@cross_origin()
def get_imports_list():
    # Appelle le service pour renvoyer l'historique des imports.
    data = service.recuperer_imports()

    # Renvoie un code 204 en cas d'absence de données.
    if not data: return '', 204

    return jsonify(data), 200

@imports_bp.route('/save/<int:id>', methods = ['POST'])
@cross_origin()
def save_import_comment(id):
    fichier = request.get_json()

    # On doit s'assurer qu'il y a bien quelque chose dans le corps de la requête (comme le nom).
    if not fichier or 'comment' not in fichier: return jsonify(fichier), 304

    service.modifier_import(id, fichier['comment'])

    return jsonify(fichier), 200

@imports_bp.route('/force-reimport', methods = ['POST'])
@cross_origin()
def importer_csv():
    # Extraction du fichier.
    file = request.files['source']
    extension = os.path.splitext(file.filename)[1]

    # Si l'extension n'est pas un fichier csv (on peut aussi se baser sur le header pour plus de sécurité mais oui rien à foutre).
    if str.lower(extension) != '.csv': return jsonify({'message': 'Format de fichier non pris en charge.'}), 400

    # Données additionnelles du formulaire.
    comment = request.form['comment']
    separator = request.form['separator'] or ','
    pool = int(request.form['pool']) or 10_000

    response = service.ajouter_import(file, comment, separator, pool)

    # Si tout s'est bien passé et que la réponse du service est vide.
    if response is None: return jsonify({'message': 'Le fichier a été tranféré avec succès.', 'uid': uuid.uuid4()}), 201
    
    # Dans le cas contraire.
    return jsonify({'message': "La requête n'a pu aboutir."}), 400