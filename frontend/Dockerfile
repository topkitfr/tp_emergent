# ── Étape 1 : Build ──────────────────────────────────────────────────────────
FROM node:20-alpine AS build

WORKDIR /app

# Copie package.json en premier pour profiter du cache Docker
COPY package.json package-lock.json ./
RUN npm ci --legacy-peer-deps

# Copie du code source
COPY . .

# L'URL du backend est injectée au build via ARG
ARG REACT_APP_BACKEND_URL=http://localhost:8000
ARG REACT_APP_API_URL=http://localhost:8000/api
ENV REACT_APP_BACKEND_URL=$REACT_APP_BACKEND_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

# ── Étape 2 : Serve avec Nginx ────────────────────────────────────────────────
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html

# Config nginx pour React Router (SPA)
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
