# Hola Mundo Fútbol

Proyecto de ejemplo con FastAPI, Bootstrap, PostgreSQL y consumo de la API de football-data.org.

## Estructura

- `main.py` - servidor FastAPI, modelo, base de datos y consumo de API.
- `templates/index.html` - frontend Bootstrap.
- `Dockerfile` - imagen de la aplicación.
- `.env.example` - variables de entorno.

## Requisitos

- Docker
- API Key de football-data.org

## Variables de entorno

Crea un archivo `.env` desde `.env.example` y establece tu API key:

```env
DATABASE_URL=postgresql://user:password@db:5432/futbol_db
FOOTBALL_API_KEY=tus_api_key_aqui
```

## Ejecución local con Docker Compose

Crea un archivo `.env` desde `.env.example` y pon tu `FOOTBALL_API_KEY`.

```bash
docker compose up --build
```

Luego abre `http://localhost:8000`.

## Construir la imagen Docker manualmente

```bash
docker build -t tu_usuario_dockerhub/hola-mundo-futbol:latest .
```

## Subir a Docker Hub

```bash
docker login
docker push tu_usuario_dockerhub/hola-mundo-futbol:latest
```

## Despliegue en AWS

Opciones rápidas:

1. AWS ECS con Fargate
   - Usa la imagen de Docker Hub.
   - Configura un servicio que consuma el puerto `8000`.
   - Añade variables de entorno `DATABASE_URL` y `FOOTBALL_API_KEY`.

2. AWS Elastic Beanstalk
   - Despliega el proyecto como aplicación Docker.
   - Configura las variables de entorno del entorno EB.

### Recomendación

- Para producción, no expongas la clave en el repositorio.
- Usa AWS Secrets Manager o Parameter Store para la clave.
- Configura una base de datos PostgreSQL gestionada (Amazon RDS).

## Endpoints

- `GET /` - página principal.
- `POST /api/fetch-teams` - trae equipos de la Premier League y los guarda en la DB.
- `GET /api/teams` - lista equipos guardados en la DB.
