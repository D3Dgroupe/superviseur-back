# app/utils/file_watcher.py
import time
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

def start_watching(path, on_created_callback, seconds = 10):
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