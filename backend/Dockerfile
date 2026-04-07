FROM python:3.11-slim

WORKDIR /app

# Dépendances système (pour certaines libs comme cryptography, pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie et install des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source dans /app/backend
COPY . ./backend

# Création du dossier uploads (persisté via volume Docker)
RUN mkdir -p /app/uploads

EXPOSE 8000

# Lance uvicorn depuis /app pour que les imports relatifs fonctionnent
CMD ["uvicorn", "backend.server:app", "--host", "0.0.0.0", "--port", "8000"]
