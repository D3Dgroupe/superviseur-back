'''
    Modèle brut pour un historique.
    models/aksm/history.py
'''
from colorama import Fore

class History():

    print(Fore.LIGHTCYAN_EX +  f'Trouvé le modèle suivant : AKSM/{__name__}.')
    
    model = '''
        CREATE TABLE IF NOT EXISTS `history` (
        `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
        `date_imported` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "Date d'importation.",
        `file_name` varchar(255) NOT NULL COMMENT "Nom du fichier importé.",
        `reading_start` datetime DEFAULT NULL COMMENT "Début des mesures.",
        `reading_end` datetime DEFAULT NULL COMMENT "Fin des mesures.",
        `nb_missing` int NOT NULL DEFAULT '0' COMMENT "Nombre de valeurs manquantes.",
        `status` int NOT NULL DEFAULT '0' COMMENT "Etat dans lequel se trouve l'importation ?",
        `comment` varchar(511) DEFAULT NULL COMMENT "Commentaire sur l'importation.",

        PRIMARY KEY (`id`)
        ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
    '''

    def __init__(self):
        print("Merci de ne pas instancier cette classe.")