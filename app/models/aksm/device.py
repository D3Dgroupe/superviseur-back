'''
    Modèle brut pour un équipement.
    models/aksm/device.py
'''

from colorama import Fore

class Device():

    print(Fore.LIGHTCYAN_EX + f'Trouvé le modèle suivant : AKSM/{__name__}.')
    
    model = '''
        CREATE TABLE IF NOT EXISTS `devices` (
        `id` int UNSIGNED NOT NULL AUTO_INCREMENT,
        `tag` varchar(255) NOT NULL DEFAULT "Inconnu" COMMENT "Tag utilisé pour la distinction.",
        `nameGtc` varchar(255) NOT NULL DEFAULT "Inconnu" COMMENT "Nom de l'équipement dans la GTC.",
        `nameDisplayed` varchar(255) NOT NULL DEFAULT "Inconnu" COMMENT "Nom affiché dans les mesures.",
        `deviceGroup` varchar(255) NOT NULL DEFAULT "Inconnu" COMMENT "Premier groupe d'appartenance pour cet équipement.",
        `deviceGroup_b` varchar(255) DEFAULT NULL COMMENT "Deuxième groupe d'appartenance pour cet équipement.",
        `deviceGroup_c` varchar(255) DEFAULT NULL COMMENT "Troisième groupe d'appartenance pour cet équipement.",
        `location` varchar(255) DEFAULT NULL COMMENT "Lieu où se trouve l'équipement.",
        `unit` varchar(32) DEFAULT NULL COMMENT "Unité dans laquelle sera prise la mesure.",
        `previsionnel` tinyint DEFAULT 0 COMMENT "Equipement générique permettant la saisie de valeurs prévisionnelles pour un équipement réel.",
        `digital` tinyint DEFAULT NULL COMMENT "Si c'est un appareil digital ou analogue.",
        `rate` tinyint DEFAULT NULL COMMENT "La fréquence des mesures.",
        `threshold` float DEFAULT NULL COMMENT "Le seuil a ne pas dépasser pour cet équipement.",
        `comment` varchar(511) DEFAULT NULL COMMENT "Commentaire sur l'équipement.",
        `created` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT "Date à laquelle cet équipement a été enregistré.",

        UNIQUE KEY `Tag` (`tag`),
        PRIMARY KEY (`id`)
        ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
    '''

    def __init__(self):
        print("Merci de ne pas instancier cette classe.")