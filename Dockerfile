FROM python:3.11-slim

WORKDIR /app

# Installer dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Important
ENV PYTHONPATH=/app

# Rendre le script d'entrypoint exécutable
RUN chmod +x entrypoint.sh

EXPOSE 8020

ENTRYPOINT ["./entrypoint.sh"]