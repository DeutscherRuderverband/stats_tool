# This file is the entry point for the Backend API Server based on flask.
# This file just provides the flask-based WSGI object called "app" by convention.

import os
from api.app import app

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
