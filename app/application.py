#!/usr/bin/env python
import logging
import os
import sys

import flask
import json_logging
from dotenv import load_dotenv
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Load and check env vars
load_dotenv()
SERVER_ENV = os.environ.get('APP_ENVIRONMENT', '').lower()
if not SERVER_ENV:
    print('FATAL - Unable to find environmental variable [APP_ENVIRONMENT] - exiting', file=sys.stderr)
    exit(1)

# Create Flask app
app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database.db')

# Logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)  # Set flask's req/resp logging to ERROR level
if SERVER_ENV == 'production':
    json_logging.init_flask(enable_json=True)
    json_logging.init_request_instrument(app)

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.propagate = False  # Avoid double-printing

# Initialize Flask plugins, etc
DB = SQLAlchemy(app)
CORS(app)


@app.get('/health')
def health_check() -> str:
    return 'OK'


if __name__ == '__main__':
    LOG.info('application reloaded')
    app.run(host='0.0.0.0')
