'''
    Ce service permet de traiter la logique des appareils enregistrés.
'''

from app.models.base import Database

def recuperer_appareils():
    '''
        Récupère les informations des appareils enregistrés.
    '''
    # Appel à la base de données dans le but de requêter les appareils (le mot clé `with` permet d'ouvrir et de fermer le curseur automatiquement).
    with Database() as db: appareils = db.find_all(f'select id, tag, nameGtc, nameDisplayed, tag, deviceGroup, location, unit, previsionnel, digital, rate, threshold, comment, created from devices order by created desc')

    # Renvoyer le dictionnaire.
    return appareils

def recuperer_appareil(id: int):
    '''
        Récupère un appareil.
    '''
    # Appel à la base de données dans le but de requêter les appareils (le mot clé `with` permet d'ouvrir et de fermer le curseur automatiquement).
    with Database() as db: appareil = db.find_one(f'select id, tag, nameGtc, nameDisplayed, tag, deviceGroup, location, unit, previsionnel, digital, rate, threshold, comment, created from devices where id = {id} order by nameGtc')

    # Renvoyer le dictionnaire.
    return appareil

def recuperer_appareil_par_nom(tag: str):
    '''
        Récupère un appareil.
    '''
    # Appel à la base de données dans le but de requêter les appareils (le mot clé `with` permet d'ouvrir et de fermer le curseur automatiquement).
    with Database() as db:

        # Requête préparée.
        query = '''
            SELECT id, tag, nameGtc, nameDisplayed, tag, deviceGroup, location, previsionnel, unit, digital, rate, threshold, comment, created
            FROM devices
            WHERE tag = UPPER(%s)
        '''

        # Exécute la requête.
        db.execute(query, (tag,))

        # Renvoyer le dictionnaire.
        return db.fetchone()

def ajouter_appareils(appareils: list):
    '''
        Ajouter une succession d'appareils, généralement lors de la récupération des données d'un fichier csv converti en json.
    '''
    with Database() as db:
        for appareil in appareils:
            # Requête paramétrée.
            query = '''
                INSERT INTO devices (tag, nameGtc, unit, digital, rate, created)
                VALUES (%s, %s, %s, %s, %s, now())
                ON DUPLICATE KEY UPDATE unit = VALUES(unit), digital = VALUES(digital), rate = VALUES(rate)
            '''

            # Exécute la requête.
            db.execute(query, (appareil['tag'], appareil['nameGtc'], appareil['unit'], appareil['digital'], appareil['rate']))

def ajouter_appareil(device):
    '''
        Ajouter un appareil depuis le client ui (device est du json).
    '''
    with Database() as db:
        # Requête paramétrée.
        query = '''
            INSERT INTO devices (tag, nameGtc, nameDisplayed, deviceGroup, unit, previsionnel, digital, rate, threshold, comment, created)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())
        '''

        # Exécute la requête.
        db.execute(query, (device['tag'], device['nameGtc'], device['nameDisplayed'], device['deviceGroup'], device['unit'], device['previsionnel'], device['digital'], device['rate'], device['threshold'], device['comment']))

def modifier_appareil(id: int, device):
    '''
        Modifie un appareil.
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

def recuperer_appareils_par_saisie(input: str):
    '''
        Récupère une liste d'appareils selon le pattern donné.
    '''
    with Database() as db:
        # Requête paramétrée.
        query = '''
            SELECT id, tag, nameGtc FROM devices WHERE tag LIKE (%s) ORDER BY nameGtc
        '''

        # Exécute la requête.
        db.cursor.execute(query, (f'%{input}%',))

        # Récupère les résultats.
        appareils = db.cursor.fetchall()

        # Renvoyer le dictionnaire.
        return appareils
    
def supprimer_appareil(id: int):
    '''
        Supprime un appareil.
    '''
    with Database() as db:
        # Requête paramétrée.
        query = '''
            DELETE FROM devices
            WHERE id = %s
        '''

        # Exécute la requête.
        db.execute(query, (id,))