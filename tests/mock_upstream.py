#!/usr/bin/env python
import json
import os
import sys

import flask
from dotenv import load_dotenv
from flask import request

# Load and check env vars
load_dotenv()
SERVER_ENV = os.environ.get('APP_ENVIRONMENT', '').lower()
if not SERVER_ENV:
    print('FATAL - Unable to find environmental variable [APP_ENVIRONMENT] - exiting', file=sys.stderr)
    exit(1)

# Create Flask app
app = flask.Flask(__name__)


@app.route('/<path:path>', methods=['POST', 'GET'])
def endpoint(path='') -> str:
    print(request.method, path)
    if request.is_json:
        print(json.dumps(request.json, indent=2))
    else:
        print(request.data)
    return 'OK'


if __name__ == '__main__':
    print('application reloaded')
    app.run(host='0.0.0.0')
