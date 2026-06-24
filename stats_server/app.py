from __future__ import annotations

import os

from flask import Flask
from flask import abort
from flask import request

from stats_server.stats import fetch_stats
from stats_server.stats import update_stats

app = Flask(__name__)
auth_secret = os.getenv("AUTH_SECRET")


@app.route("/stats", methods=["GET", "POST"])
def stats():
    if auth_secret and request.headers.get("Authorization") != auth_secret:
        abort(401)
    if request.method == "POST":
        update_stats(
            competition_id=request.args.get("competitionUid", ""),
            data=request.get_json(),
        )
        return {"status": "ok"}
    elif request.method == "GET":
        return fetch_stats(
            competition_id=request.args["competitionUid"],
            players=request.args["player[]"].split(","),
            maps=request.args["mapUid[]"].split(","),
        )
    abort(400)
