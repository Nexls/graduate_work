FROM python:3.8.5-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
COPY . /app
EXPOSE 8002
ENTRYPOINT gunicorn --log-level=debug --reload --bind 0.0.0.0:8002 wsgi_app:app
