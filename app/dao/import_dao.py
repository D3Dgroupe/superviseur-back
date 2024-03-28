from app.models.base import Database

class ImportDao():
    '''
        Classe permettant la gestion des accès à la base de données pour les imports.
    '''
    def __init__(self):
        print("Initialisation du `Import` Data Access Object (DAO).")

    def find_all(self):
        '''
            Récupère l'historique de tous les imports depuis la base de données.
        '''
        # Appel à la base de données dans le but de requêter les appareils (le mot clé `with` permet d'ouvrir et de fermer le curseur automatiquement).
        with Database() as db:
            historique = db.find_all(f'select date_imported, file_name, reading_start, reading_end, nb_missing, status, comment from history order by date_imported desc')

        # Renvoyer le dictionnaire.
        return historique

    def add(self, name, start = None, end = None, missing = 0, comment = None):
        '''
            Ajout de cet import en base de données.
            En gros pour laisser une trace de l'importation.
        '''
        with Database() as db:
            query = '''
                INSERT INTO history (date_imported, file_name, reading_start, reading_end, nb_missing, status, comment)
                VALUES (now(), %s, %s, %s, %s, 1, %s)
            '''

            # Exécute la requête.
            db.execute(query, (name, start, end, missing, comment))

    def sauvegarder(self, id: int, comment: str):
        '''
            Ajoute une trace de cet import en base de données.
        '''
        with Database() as db:
            query = '''
                UPDATE history
                SET comment = %s
                WHERE id = %s
            '''

            # Exécute la requête.
            db.execute(query, (comment, id))