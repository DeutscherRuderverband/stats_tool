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

### (Preparation) Install required packages

    pip install -r requirements.txt

### Database (PostgreSQL)

- **[doc/DATABASE.md](doc/DATABASE.md)** describes how to
    - run a development PostgreSQL based on `docker-compose`
    - initialize tables
- **[backend/README.md](backend/README.md)** describes how to
    - grab data from World Rowing API
- **[backend/model/README.md](backend/model/README.md)** describes how to
    - create/drop tables
    - insert data

### Backend Scrape/Maintenance Process (Python)

    python scraper.py

### Backend API Server (Python/Flask)

*Note: `pwd` is `backend/`*

```sh
python -m flask --app api_server:app run
```

Alternatively with `python api_server.py`

Debug with hot reload:

```sh
python -m flask --app api_server:app --debug run
```

**Note** Do not use this command for deployment. Use something like `gunicorn`.

### Frontend (Node.js/Vue)

- **frontend/README.md** describes how to
    - install required packages
    - run the frontend



## MVP
What would be the MVP for the customer?


## Idea's

### Database
#### Postgress vs. MySQL
https://blog.devart.com/postgresql-vs-mysql.html#:~:text=Performance%20and%20speed,concurrency%20$

#### Postgress data persistence in docker
https://stackoverflow.com/questions/41637505/how-to-persist-data-in-a-dockerized-postgres-databas$





### Plotting
Generally, we have to ask ourselves, where we want to create the plots that are supposed to be shown to the analysts.
On a broder scale, there are two options:
- create the plots in python
- create the plots in javascript
Most certainly, both options would have their benefits / drawbacks with them.

#### In Python
##### Libraries
matplotlib, seaborn

### In JS
##### Libraries
???