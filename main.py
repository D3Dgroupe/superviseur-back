# main.py
from app import create_app

# Création de l'application web.
app = create_app()

if __name__ == '__main__':
    '''
        Point de démarrage en environnement de développement.
        Test 8Recent. 
    '''

    # Attention : Bloquant (ne rien exécuter après cette ligne).
    app.run(debug = app.config['DEBUG'], use_reloader = False)