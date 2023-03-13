# drv-project
Container for the innovation project WS '22

## Deployment on Railway.app

See: [doc/DEPLOYMENT.md](doc/DEPLOYMENT.md)

## Database: Backup & Restore

See: [doc/DATABASE.md](doc/DATABASE.md)

## How to run things with Docker (dev)

Start all the services with

```sh
docker compose up
```

Start only a specific service e.g. frontend: `docker compose up frontend`

Reset the project by composing down:

```sh
docker compose down --rmi all --volumes
```

## How to run things manually

*Note that `.vscode` directory contains some useful debug configurations.*

### (Preparation) Install required packages for the backend

Using Python (at least v3.10), install all requirements.txt

    pip install -r api.requirements.txt
    pip install -r scraper.requirements.txt

### Database (PostgreSQL)

- **[doc/DATABASE.md](doc/DATABASE.md)** describes how to
    - Backup & restore
    - run a development PostgreSQL based on `docker-compose`
    - initialize tables
- **[backend/README.md](backend/README.md)** describes how to
    - grab data from World Rowing API
- **[backend/model/README.md](backend/model/README.md)** describes how to
    - create/drop tables
    - insert competition data

### Backend Scrape/Maintenance Process (Python)

*Note: Working directory (cwd) is `backend/`*

    python scraper.py

### Backend API Server (Python/Flask)

*Note: Working directory (cwd) is `backend/`*

```sh
python -m flask --app api_server:app run
```

Alternatively with `python api_server.py`

Debug with hot reload:

```sh
python -m flask --app api_server:app --debug run
```

**Note** Do not use this command for deployment. Use something like `waitress` or `gunicorn`.

### Frontend (Node.js/Vue)

- **[frontend/README.md](frontend/README.md)** describes how to
    - install required packages
    - run the frontend
