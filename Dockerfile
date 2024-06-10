FROM python:3.10-slim-bullseye

RUN mkdir /app

WORKDIR /app

COPY dist/requirements.txt /app/requirements.txt

RUN apt update && \
    apt install build-essential libpq-dev -y && \
    pip3 install -r requirements.txt && \
    apt autoremove build-essential -y && \
    apt clean

COPY dist/ /app/

EXPOSE 8000

CMD uvicorn main:app --reload --log-level info --host 0.0.0.0 --port 8000
# CMD gunicorn main:app --worker-class uvicorn.workers.UvicornWorker --workers 3 --bind 0.0.0.0:8000
