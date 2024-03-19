import os
import time
import requests
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
from colorama import Fore

def mailing(e: str, url: str):
    '''
        Envoi une alerte par mail au destinataire.\n
        Exécuté uniquement lors d'une mise en production.
    '''
    print(f"Envoi d'un mail d'alerte pour le service `{url}`...")

    try:
        # Variables extraites depuis l'environnement.
        sender = os.getenv('SENDER')
        receiver = os.getenv('RECEIVER')

        smtp_host = os.getenv('SMTP_SERVER')
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        
        # Paramètres.
        message = MIMEText(f"On dirait qu'un des services a pété une durite, voyez par vous même les informations complémentaires ci-dessous : \n {e}", "plain")
        message["Subject"] = f"Le service à l'adresse {url} a cessé de fonctionner."
        message["From"] = sender
        message["To"] = receiver

        # Connexion sécurisée avec le serveur.
        server = SMTP(smtp_host)
        server.set_debuglevel(False)
        server.login(smtp_username, smtp_password)

        # Envoyer l'email.
        try: server.sendmail(sender, receiver, message.as_string())
        finally: server.quit()
    except:
        print(f"Echec de l'envoi d'un email d'alerte.")

def ping_service():
    '''
        Permet de ping les deux services.\n
        Exécuté uniquement lors d'une mise en production.
    '''
    influx = os.getenv('INFLUXDB_HOST', 'http://localhost:8086')
    grafana = os.getenv('GRAFANA_HOST', 'http://localhost:3000')

    try:
        # Exécute la requête.
        response = requests.get(influx)
        
        # Traiter cette partie car si la configuration du service est mauvaise on aura potentiellement autre chose qu'un code 200.
        if response.status_code != 200: print(f"Le service a renvoyé le statut suivant : {response.status_code}.")
    except requests.exceptions.RequestException as e:
        mailing(e, influx)

    try:
        # Exécute la requête.
        response = requests.get(grafana)
        
        # Traiter cette partie car si la configuration du service est mauvaise on aura potentiellement autre chose qu'un code 200.
        if response.status_code != 200: print(f"Le service a renvoyé le statut suivant : {response.status_code}.")
    except requests.exceptions.RequestException as e:
        mailing(e, grafana)

def run_periodic_pings(interval, env: str):
    '''
        Effectue des pings périodiquement par l'interval spécifié pour assurer le bon fonctionnement des services critiques.\n
        @source la source où sera émis le ping, en cas d'environnement de test, le ping ne sera pas émis.
    '''
    while True:
        if (env == 'PRODUCTION'): ping_service()
        time.sleep(interval)
