# app/exceptions/errors.py
from flask import jsonify

# Prototype.
class NotFoundError(Exception): pass

# Prototype.
class InternalError(Exception): pass

def not_found_error(error):
    return jsonify({"error": "404", "message": "La ressource demandée est introuvable."}), 404

def internal_error(error):
    return jsonify({"error": "500", "message": "Quelque chose ne s'est pas passé comme prévu."}), 500