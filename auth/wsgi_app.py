# flask_app/wsgi_app.py
from gevent import monkey
monkey.patch_all()

from main import app
