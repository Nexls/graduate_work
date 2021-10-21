FROM python:3.9.1-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
COPY . /app
EXPOSE 8003
ENTRYPOINT uvicorn --host 0.0.0.0 --port 8003 --log-config gunicorn_logging.conf app:app