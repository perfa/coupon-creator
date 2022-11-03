#!/usr/bin/env python
import logging
import os
import sys

import flask
import json_logging
from dotenv import load_dotenv
from flask_cors import CORS
from flask_migrate import Migrate

import models
from app.brand import blueprint as brand_bp
from app.fan import blueprint as fan_bp

# Load and check env vars
load_dotenv()
SERVER_ENV = os.environ.get('APP_ENVIRONMENT', '').lower()
if not SERVER_ENV:
    print('FATAL - Unable to find environmental variable [APP_ENVIRONMENT] - exiting', file=sys.stderr)
    exit(1)

# Create Flask app
app = flask.Flask(__name__)
app.register_blueprint(brand_bp, url_prefix='/brands')
app.register_blueprint(fan_bp, url_prefix='/fans')


# Logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)  # Set flask's req/resp logging to ERROR level
if SERVER_ENV == 'production':
    json_logging.init_flask(enable_json=True)
    json_logging.init_request_instrument(app)

LOG = logging.getLogger(__name__)
LOG.addHandler(logging.StreamHandler(sys.stdout))
LOG.propagate = False  # Avoid double-printing

# Initialize Flask plugins, etc
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '../database.db')
models.db_root.init_app(app)
migration = Migrate(app, models.db_root)  # Initialize flask-migrate
CORS(app)


@app.get('/health')
def health_check() -> str:
    """Minimal endpoint for ECS/k8s health checks"""
    return 'OK'


if __name__ == '__main__':
    LOG.info('application reloaded')
    app.run(host='0.0.0.0')
