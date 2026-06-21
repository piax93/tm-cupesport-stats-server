FROM    python:3.14-alpine

WORKDIR /code

COPY    requirements.txt ./
RUN     pip install --no-cache-dir -r requirements.txt

COPY    stats_server ./stats_server

RUN     mkdir -p /.gunicorn && chown nobody:nogroup /.gunicorn

USER    nobody
EXPOSE  8080
CMD     [ "python", "-m", "gunicorn", "--workers", "4", "--bind", "0.0.0.0:8080", "stats_server.app:app" ]
