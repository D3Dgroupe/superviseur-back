# app/routes.py
from flask import Flask

def register_routes(app: Flask):
    # Imports.
    from .controller.imports import imports_bp
    from .controller.devices import devices_bp
    from .controller.inputs import inputs_bp
    from .controller.suppression import suppression_bp
    
    # Enregistre les routes spécifiques au serveur.
    app.register_blueprint(imports_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(inputs_bp)
    app.register_blueprint(suppression_bp)

    # Importer d'autres routes ici.
    # ...