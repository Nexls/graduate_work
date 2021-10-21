FROM python:3.9.1-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
COPY . /app
EXPOSE 8002
ENTRYPOINT gunicorn --log-level=debug --log-config gunicorn_logging.conf --reload --bind 0.0.0.0:8002 wsgi_app:app
