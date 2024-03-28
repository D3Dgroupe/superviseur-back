# app/services/import_service.py
import os
from dotenv import load_dotenv
from werkzeug.datastructures import FileStorage
from app.dao.import_dao import ImportDao
from app.dao.device_dao import DeviceDao
from app.utils.csv_to_json import convert
from app.utils.influx import transmute

class ImportService():
    '''
        Service de gestion des imports.
    '''
    def __init__(self):
        print("Initialisation de `Import` Service.")
        self.import_dao = ImportDao()
        self.device_dao = DeviceDao()
        
        # Le fichier .env local en cas de développement.
        if os.environ.get('FLASK_ENV', 'DEVELOPMENT') == 'DEVELOPMENT': load_dotenv()

    def recuperer_imports(self):
        data = self.import_dao.find_all()
        return data

    def ajouter_import(self, file: FileStorage, comment: str, separator: str, pool: int):
        # Remonte au dossier racine ./app (ce fichier se trouve dans ./app/routes)
        destination = os.path.join(os.environ.get('UPLOAD_FOLDER'), file.filename)
        
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
            # TODO : Pas vraiment un todo mais il faut savoir qu'on ouvre et ferme la connexion à chaque fois dans notre boucle.
            # En principe ce n'est pas un problème au vu de notre utilisation, mais c'est une piste d'amélioration pour l'avenir.
            eq_full = self.device_dao.find_by_tag(eq['tag'])
            
            # On ne mettra pas à jour le dictionnaire si le tag du csv n'existe pas en base de données.
            if eq_full is None: continue

            # Met à jour le dictionnaire (rappelons que chaque équipement possède une liste de mesures).
            eq.update({"tag": eq_full['tag']})
            eq.update({"nameGtc": eq_full['nameGtc']})
            eq.update({"nameDisplayed": eq_full['nameDisplayed']})
            eq.update({"unit": eq_full['unit']})
            eq.update({"threshold": eq_full['threshold']})

            # Les groupes.
            eq.update({"deviceGroup": eq_full['deviceGroup']})

            # Push ce dictionnaire dans la liste.
            equipments.append(eq)

        # Envoi les données capteurs valides vers influx db.
        transmute(equipments, pool)

        # Si tout se passe bien, on appelle le service pour ajouter une trace de cet import en base de données.
        self.import_dao.add(file.filename, start = data['start'], end = data['end'], missing = data['missing'], comment = comment)

    def modifier_import(self, id: int, comment: str):
        self.import_dao.sauvegarder(id, comment)