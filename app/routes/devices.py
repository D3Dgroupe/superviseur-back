# app/routes/history.py
import hashlib
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services.device_service import *
from app.utils.influx import purge

'''
    Ce fichier représente une route serveur.
'''

devices_bp = Blueprint('devices', __name__, url_prefix = '/devices')

@devices_bp.route('/', methods = ['GET'])
@cross_origin()
def get_devices():
    # Appelle le service pour renvoyer les appareils.
    data = recuperer_appareils()

    # Renvoie un code 204 en cas d'absence de données.
    if not data: return '', 204

    return jsonify(data), 200

@devices_bp.route('/<int:id>', methods = ['GET'])
@cross_origin()
def recuperer_capteur(id: int):
    # Appelle le service pour renvoyer les appareils.
    capteur = recuperer_appareil(id)

    # Renvoie un code 204 en cas d'absence de données.
    if not capteur: return '', 204

    return jsonify(capteur), 200

@devices_bp.route('/<string:input>/find', methods = ['GET'])
@cross_origin()
def find_devices_by_input(input: str):
    '''
        Cet end point permet de récupérer une liste de capteurs selon la chaine récupérée.
    '''
    # On doit s'assurer qu'il y a bien quelque chose dans le corps de la requête (comme le nom ou l'id).
    if not input or len(input) < 3: return '', 204

    # Appelle le service pour ajouter le capteur (data correspond au modèle device).
    appareils = recuperer_appareils_par_saisie(input)

    # Renvoie un statut code (créé) et le capteur ajouté (il faudrait avoir un callback côté service car là on reprend ce qui a été envoyé).
    return jsonify(appareils), 200

@devices_bp.route('/add', methods = ['POST'])
@cross_origin()
def ajouter_device():
    capteur = request.get_json()

    # Validation (qu'on devrait réaliser dans une couche validation).
    capteur_validation = {
        'tag': capteur.get('tag'),
        'nameGtc': capteur.get('nameGtc'),
        'nameDisplayed': capteur.get('nameDisplayed'),
        'deviceGroup': capteur.get('deviceGroup'),
        'unit': capteur.get('unit', None),
        'previsionnel': capteur.get('previsionnel', None),
        'digital': capteur.get('digital', None),
        'rate': capteur.get('rate', None),
        'threshold': capteur.get('threshold', None),
        'comment': capteur.get('comment', None)
    }

    # On vire les espaces blancs en début et fin de chaque entrée si c'est une chaîne.
    trimmed = {key: value.strip() if isinstance(value, str) else value for key, value in capteur_validation.items()}

    # On doit s'assurer qu'il y a bien quelque chose dans le corps de la requête (comme le nom).
    if not capteur or 'tag' not in capteur: return jsonify(capteur), 400

    # Vérifie que le nom n'est pas déjà utilisé par un autre capteur existant.
    capteurExistant = recuperer_appareil_par_nom(capteur['tag'])

    # Si le capteur existe déjà.
    if capteurExistant: return jsonify(f"Ce tag est déjà utilisé par le capteur `{capteurExistant['nameGtc']}`."), 400

    # Appelle le service pour ajouter le capteur (data correspond au modèle device).
    ajouter_appareil(trimmed)

    # Renvoie un statut code (créé) et le capteur ajouté (il faudrait avoir un callback côté service car là on reprend ce qui a été envoyé).
    return jsonify(capteur), 201

@devices_bp.route('/<int:id>/update', methods = ['PUT'])
@cross_origin()
def modifier_device(id: int):
    capteur = request.get_json()

    # On doit s'assurer qu'il y a bien quelque chose dans le corps de la requête (comme le nom).
    if not capteur or 'id' not in capteur: return jsonify(capteur), 400

    # Appelle le service pour ajouter le capteur (data correspond au modèle device).
    modifier_appareil(id, capteur)

    # Renvoie un statut code (créé) et le capteur ajouté (il faudrait avoir un callback côté service car là on reprend ce qui a été envoyé).
    return jsonify(capteur), 200

@devices_bp.route('/<int:id>/<string:tag>/delete', methods = ['DELETE'])
@cross_origin()
def supprimer_device(id: int, tag: str):
    # Tente d'abord de supprimer tous les points dans influx avant de le supprimer de mysql.
    purge(tag)
    
    # Supprime l'appareil.
    supprimer_appareil(id)

    # Renvoie un statut code (créé) et le capteur ajouté (il faudrait avoir un callback côté service car là on reprend ce qui a été envoyé).
    return jsonify('Appareil supprimé avec succès.'), 200