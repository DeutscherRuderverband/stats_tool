# Deployment on Railway.app

References:
- https://docs.railway.app/
- https://docs.railway.app/deploy/monorepo
- https://docs.railway.app/develop/variables

## Database (PostgreSQL)

**Step:** Add a PostgreSQL database to your project's environment on *railway.app*.

*Note that the connection credentials of the database will be automatically provided to the services by *railway.app* via environment variables. So no further steps are necessary.*

## Backend API

The following **service settings** have to be made on *railway.app*:

**Step 1:** Set *Root Directory* as follows
```
/backend
```

**Step 2:** Set *Build Command* as follows
```
pip install -r api.requirements.txt
```

**Step 3:** Set *Start Command* as follows
```
python -m waitress --host 0.0.0.0 --port ${PORT} api_server:app
```

Notes:

The Python version is configured by code in `runtime.txt`. See: https://github.com/railwayapp/nixpacks/tree/main/examples/python-2-runtime


## Backend Scraper

The following **service settings** have to be made on *railway.app*:

**Step 1:** Set *Root Directory* as follows
```
/backend
```

**Step 2:** Set *Build Command* as follows
```
pip install -r scraper.requirements.txt
```

**Step 3:** Set *Start Command* as follows
```
python scraper.py
```

Notes:

The Python version is configured by code in `runtime.txt`. See: https://github.com/railwayapp/nixpacks/tree/main/examples/python-2-runtime


## Frontend

The following **service settings** have to be made on *railway.app*:

**Step 1:** Set *Root Directory* as follows

```
/frontend
```

**Step 2**

Set the environment variable `VITE_BACKEND_API_BASE_URL` to tell the *frontend* how to connect to the Backend API. To do this you have to find out the public (!) URL of the Backend API. The following is just an **example**:

```
VITE_BACKEND_API_BASE_URL=https://backend-api-production-drv-project.up.railway.app
```


Notes:

- The Node.js version is configured by code in `package.json`
    - See `"engines": {"node": "16" }`