import logging
import sys
from datetime import timedelta
from logging import config

import json_logging
import settings
from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS
from oauth.outhservice import oauth_service
from requests import post
from utils import context_logger

app = Flask(__name__)
app.config['JWT_PRIVATE_KEY'] = settings.private_key
app.config['JWT_PUBLIC_KEY'] = settings.public_key
app.config['JWT_ALGORITHM'] = 'RS256'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=settings.access_token_expires)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(seconds=settings.refresh_token_expires)
CORS(app, resources={r"/*": {"origins": "*"}})

json_logging.ENABLE_JSON_LOGGING = True
json_logging.init_flask(enable_json=True)

logger = context_logger.get(__name__)
config.dictConfig(settings.LOGGING)
logger.logger.addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger('flask_cors').level = logging.DEBUG


@app.route('/')
def index():
    return render_template('index.html')


def is_human(client_key: str):
    payload = {'secret': settings.RECAPTCHA_SECRET_KEY, 'response': client_key}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    res = post('https://www.google.com/recaptcha/api/siteverify', data=payload, headers=headers)
    return res.json()['success']


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        url_direct = request.json['url']
        client_key = request.json['g_recaptcha']
        if not client_key or is_human(client_key):
            return redirect(url_for(url_direct), code=307)
        else:
            return redirect(url_for('login'), code=301)
    return render_template('login.html', oauth_urls=oauth_service.providers_list, account=None,
                           client_secret=settings.RECAPTCHA_SITE_KEY)


app.add_url_rule('/social_auth/<string:method>/<string:provider_name>', 'social_auth', oauth_service.oauth_resolver)
