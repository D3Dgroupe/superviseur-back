from app.models.base import Database

class DeviceDao():
    '''
        Classe permettant la gestion des accès à la base de données pour les capteurs.
    '''
    def __init__(self):
        print("Initialisation du `Device` Data Access Object (DAO).")

    def find_all(self):
        '''
            Récupère la liste des appareils enregistrés.
        '''
        with Database() as db:
            # Appel à la base de données dans le but de requêter les appareils (le mot clé `with` permet d'ouvrir et de fermer le curseur automatiquement).
            appareils = db.find_all(f'select id, tag, nameGtc, nameDisplayed, tag, deviceGroup, location, unit, previsionnel, digital, rate, threshold, comment, created from devices order by created desc')

            # Renvoyer le dictionnaire.
            return appareils
    
    def find_by_tag(self, tag: str):
        '''
            Récupère un équipement par son tag.\n
            Le tag correspond à notre stratégie pour identifier un appareil.
        '''

        with Database() as db:
            # Requête préparée.
            query = '''
                SELECT id, tag, nameGtc, nameDisplayed, tag, deviceGroup, location, unit, previsionnel, digital, rate, threshold, comment, created
                FROM devices
                WHERE tag = UPPER(%s)
            '''

            # Exécute la requête.
            db.execute(query, (tag,))

            # Renvoyer le dictionnaire.
            return db.fetchone()
        
    def create(self, device: dict):
        '''
            Ajoute (sauvegarde) un nouvel appareil.
        '''
        with Database() as db:
            # Requête paramétrée.
            query = '''
                INSERT INTO devices (tag, nameGtc, nameDisplayed, deviceGroup, unit, previsionnel, digital, rate, threshold, comment, created)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())
            '''

            # Exécute la requête.
            db.execute(query, (device['tag'], device['nameGtc'], device['nameDisplayed'], device['deviceGroup'], device['unit'], device['previsionnel'], device['digital'], device['rate'], device['threshold'], device['comment']))

    def save(self, id: int, device: dict):
        '''
            Sauvegarde un appareil existant.
        '''
        with Database() as db:
            # Requête paramétrée.
            query = '''
                UPDATE devices
                SET tag = %s, nameGtc = %s, nameDisplayed = %s, deviceGroup = %s, unit = %s, previsionnel = %s, digital = %s, rate = %s, threshold = %s, comment = %s
                WHERE id = %s
            '''

            # Exécute la requête.
            db.execute(query, (device['tag'], device['nameGtc'], device['nameDisplayed'], device['deviceGroup'], device['unit'], device['previsionnel'], device['digital'], device['rate'], device['threshold'], device['comment'], id))

    def save_all(self, devices: list):
        '''
            Ajoute (sauvegarde) une liste d'appareils.
        '''
        with Database() as db:
            for appareil in devices:
                # Requête paramétrée.
                query = '''
                    INSERT INTO devices (tag, nameGtc, unit, digital, rate, created)
                    VALUES (%s, %s, %s, %s, %s, now())
                    ON DUPLICATE KEY UPDATE unit = VALUES(unit), digital = VALUES(digital), rate = VALUES(rate)
                '''

                # Exécute la requête.
                db.execute(query, (appareil['tag'], appareil['nameGtc'], appareil['unit'], appareil['digital'], appareil['rate']))

    def find_by_id(self, id: int):
        '''
            Recherche un appareil par son identifiant.
        '''
        # Appel à la base de données dans le but de requêter les appareils (le mot clé `with` permet d'ouvrir et de fermer le curseur automatiquement).
        with Database() as db:
            appareil = db.find_one(f'select id, tag, nameGtc, nameDisplayed, tag, deviceGroup, location, unit, previsionnel, digital, rate, threshold, comment, created from devices where id = {id} order by nameGtc')

        # Renvoyer le dictionnaire.
        return appareil
    
    def find_all_like_tag(self, tag: str):
        '''
            Recherche une série d'appareils par leur tag.
        '''
        with Database() as db:
            # Requête paramétrée.
            query = '''
                SELECT id, tag, nameGtc FROM devices WHERE tag LIKE (%s) ORDER BY nameGtc
            '''

            # Exécute la requête.
            db.cursor.execute(query, (f'%{tag}%',))

            # Récupère les résultats.
            appareils = db.cursor.fetchall()

            # Renvoyer le dictionnaire.
            return appareils
        
    def delete(self, id: int):
        '''
            Supprime un appareil par son identifiant.
        '''
        with Database() as db:
            # Requête paramétrée.
            query = '''
                DELETE FROM devices
                WHERE id = %s
            '''

            # Exécute la requête.
            db.execute(query, (id,))