FROM    python:3.14-alpine

WORKDIR /code

COPY    requirements.txt ./
RUN     pip install --no-cache-dir -r requirements.txt

COPY    stats_server ./

CMD     [ "python", "-m", "stats_server.app" ]
