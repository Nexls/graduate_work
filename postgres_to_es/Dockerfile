FROM python:3.8.5-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
COPY . /app
ENTRYPOINT python3 postgres_to_es.py