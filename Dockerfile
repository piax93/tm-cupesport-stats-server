FROM    python:3.14-alpine

WORKDIR /code

COPY    requirements.txt ./
RUN     pip install --no-cache-dir -r requirements.txt

COPY    stats_server ./stats_server

RUN     mkdir -p /.gunicorn && chown nobody:nogroup /.gunicorn

RUN     mkdir -p /data && chmod a+w /data
ENV     DATABASE_DIRECTORY=/data
VOLUME  /data

USER    nobody
EXPOSE  8080

ENV     GUNICORN_CMD_ARGS="--workers=4 --bind=0.0.0.0:8080 --access-logfile=-"

CMD     [ "python", "-m", "gunicorn", "stats_server.app:app" ]
