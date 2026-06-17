# CupEsport Stats Server
API server compatible with the CupEsport Trackmania game mode.

### How-to run
The easiest way to run this by using the container image available in Dockerhub:
```bash
docker run --rm -e AUTH_SECRET=... -p 8080:8080 piax93/tm-cupesport-stats-server
```

### How-to connect
When using the `TM_CupEsport_Online.Script.txt` mode, you can set the following to collect tournament statistics:
* `S_TournamentStatsApiUrl`: URL where the stats server is being hosted;
* `S_TournamentStatsApiCompetitionUid`: unique identifier for the compentition;
* `S_TournamentStatsApiAuthorizationHeader`: authentication secret set for the API server.
