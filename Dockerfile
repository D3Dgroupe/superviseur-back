FROM python:3.10-slim

# Le répertoire où se situera notre application (répertoire de travail).
WORKDIR /app

# Installer les dépendances.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Installer CURL.
RUN apt-get update && apt-get install -y curl

# Copier le code de l'application.
COPY . .

# Exposer le port.
EXPOSE 9090

# Démarrer l'application (production).
CMD ["gunicorn", "--config", "app/config/gunicorn.py", "main:app"]