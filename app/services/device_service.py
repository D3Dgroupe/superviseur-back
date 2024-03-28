from app.dao.device_dao import DeviceDao
from app.models.base import Database

class DeviceService():
    '''
        Service de gestion des capteurs.
    '''
    def __init__(self):
        print("Initialisation de `Device` Service.")
        self.device_dao = DeviceDao()

    def recuperer_appareils(self):
        '''
            Récupère la liste des appareils enregistrés.
        '''
        return self.device_dao.find_all()

    def recuperer_appareil(self, id: int):
        '''
            Récupère un appareil par son identifiant.
        '''
        return self.device_dao.find_by_id(id)

    def recuperer_appareil_par_tag(self, tag: str):
        '''
            Récupère un équipement par son tag.\n
            Le tag correspond à notre stratégie pour identifier un appareil.
        '''
        return self.device_dao.find_by_tag(tag)

    def importer_appareils(self, appareils: list):
        '''
            Ajouter des appareils, se produit par exemple lors de la récupération des données d'un fichier csv converti en json.
        '''
        self.device_dao.save_all(appareils)

    def ajouter_appareil(self, device: dict):
        '''
            Ajoute (sauvegarde) un nouvel appareil.
        '''
        self.device_dao.create(device)

    def modifier_appareil(self, id: int, device):
        '''
            Sauvegarde un appareil existant.
        '''
        self.device_dao.save(id, device)

    def recuperer_appareils_par_saisie(self, input: str):
        '''
            Recherche une série d'appareils par leur tag.
        '''
        return self.device_dao.find_all_like_tag(input)
        
    def supprimer_appareil(self, id: int):
        '''
            Supprime un appareil par son identifiant.
        '''
        self.device_dao.delete(id)