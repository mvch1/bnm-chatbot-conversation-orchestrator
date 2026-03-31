FROM python:3.11-slim

WORKDIR /app

# Installer dépendances
COPY conversation-orchestrator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code


# Important
ENV PYTHONPATH=/app

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]