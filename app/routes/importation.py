# app/routes/importation.py
import os
import uuid
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from app.services import historique_service, device_service
from app.utils.csv_to_json import convert
from app.utils.influx import transmute

# On appelle load_dotenv() pour les venv locales en mode développement, autrement celles du docker compose.
if os.environ.get('FLASK_ENV', 'DEVELOPMENT') == 'DEVELOPMENT': load_dotenv()

importation_bp = Blueprint('importation', __name__, url_prefix = '/imports')

@importation_bp.route('/force-reimport', methods = ['POST'])
@cross_origin()
def importer_csv():
    # Extraction du fichier.
    file = request.files['source']
    extension = os.path.splitext(file.filename)[1]

    # Données additionnelles.
    comment = request.form['comment']
    separator = request.form['separator'] or ','
    pool = request.form['pool'] or 10_000

    # Remonte au dossier racine ./app (ce fichier se trouve dans ./app/routes)
    destination = os.path.join(os.environ.get('UPLOAD_FOLDER'), file.filename)

    # Si l'extension n'est pas un fichier csv (on peut aussi se baser sur le header pour plus de sécurité).
    if str.lower(extension) != '.csv': return jsonify({'message': 'Format de fichier non pris en charge.'}), 400
    
    if file:
        # Sauvegarde dans le répertoire uploads (et non dans celui surveillé par le watch dog).
        file.save(destination)

        # Converti le fichier nouvellement uploadé en dictionnaire.
        data = convert(destination, separator = separator)

        # Renvoie ce statut code si aucune donnée n'a été convertie.
        if data == None: return 400

        # Les équipements dont on va pull les infos depuis MySQL.
        equipments = []

        # On parcours les équipements du csv et on vérifie leur présence dans la base de données pour en extraire les infos.
        for eq in data['equipements']:
            # Récupère les informations au complet de l'appareil.
            eq_full = device_service.recuperer_appareil_par_nom(eq['tag'])
            
            # On ne mettra pas à jour le dictionnaire si le tag du csv n'existe pas en base de données.
            if eq_full is None: continue

            # Met à jour le dictionnaire.
            eq.update({"tag": eq_full['tag']})
            eq.update({"nameGtc": eq_full['nameGtc']})
            eq.update({"nameDisplayed": eq_full['nameDisplayed']})
            eq.update({"unit": eq_full['unit']})
            eq.update({"previsionnel": eq_full['previsionnel']})
            eq.update({"threshold": eq_full['threshold']})

            # Les groupes.
            eq.update({"deviceGroup": eq_full['deviceGroup']})

            # Push ce dictionnaire dans la liste.
            equipments.append(eq)

        # Envoi les données capteurs valides vers influx db.
        transmute(equipments, pool)

        # Si tout se passe bien, on appelle le service pour ajouter une trace de cet import en base de données.
        historique_service.ajouter_trace(file.filename, start = data['start'], end = data['end'], missing = data['missing'], comment = comment)

        # Renvoie la réponse au client.
        return jsonify({'message': 'Le fichier a été tranféré avec succès.', 'uid': uuid.uuid4()}), 201
    
    # Dans le cas où on a pas de fichier propre.
    return jsonify({'message': "Une erreur est survenue."}), 400