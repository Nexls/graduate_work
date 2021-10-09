FROM python:3.8.5-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt
COPY . /app
EXPOSE 8000
ENTRYPOINT uvicorn --host 0.0.0.0 --port 8000 main:app