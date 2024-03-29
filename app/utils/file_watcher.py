# app/utils/file_watcher.py
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from colorama import Fore

class WatchdogEventHandler(FileSystemEventHandler):
    '''
        Classe permettant de gérer un mécanisme d'événement de type watchdog (chien de garde).
        Lorsqu'un nouveau fichier est découvert on appelle la procédure callback (on_created_callback).
    '''
    # Constructeur.
    def __init__(self, on_created_callback):
        print(Fore.CYAN + "Démarrage du watch dog en attente de fichiers entrants...")
        self.on_created_callback = on_created_callback

    # Appelée automatiquement lorsqu'un fichier ou dossier est créé.
    def on_created(self, event):
        # Vérifie que l'événement concerne un fichier.
        if not event.is_directory: self.on_created_callback(event.src_path)

def start_watching_linux(path, on_created_callback, seconds = 10):
    # Démarre le gestionnaire.
    event_handler = WatchdogEventHandler(on_created_callback = on_created_callback)
    
    # Démarre l'observateur et exécute les instructions en réponse à un événement.
    observer = Observer()
    observer.schedule(event_handler, path, recursive = False)
    observer.start()
    
    try:
        # Boucle infinie (contrôlée).
        while True: time.sleep(int(seconds))
    # Interrompt le processus après une interruption utilisateur (exemple CTRL C avec linux).
    except KeyboardInterrupt:
        observer.stop()
    
    # Permet de joindre thread (comme pour asyncio) et attend la fermeture de celui-ci.
    observer.join()

def start_watching_windows(folder_path, callback_function, scan_interval):
    # On initialise le set avec les fichiers qui ont déjà été traités dans le répertoire (en cas de crash par exemple).
    last_files = set(os.listdir(folder_path))


    while True:
        # Récupère les fichiers déjà présents.
        current_files = set(os.listdir(folder_path))
        
        # Fait la comparaison avec les derniers fichiers.
        new_files = current_files - last_files

        # Pour chaque nouveau fichier on bascule vers le callback pour import.
        for filename in new_files: callback_function(f'{folder_path}/{filename}')

        # Met à jour la liste des derniers fichiers.
        last_files = current_files.copy()

        # TODO : On zip + déplace le fichier traité ?
        
        # Délai avant prochain tour de boucle.
        time.sleep(scan_interval)