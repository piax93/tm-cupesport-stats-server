from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

from stats_server.types import TournamentStats
from stats_server.types import PlayerStats
from stats_server.database import Player
from stats_server.database import PlayerRecord
from stats_server.database import TournamentRecord
from stats_server.database import session


def update_stats(compention_id: str, data: TournamentStats) -> None:
    compention_id = compention_id or data["competitionUid"]
    with session.begin() as s:
        stmt = sqlite_upsert(Player).values(
            [
                dict(
                    compention_id=compention_id,
                    player_id=player_id,
                    top1=stats["top1"],
                    cumucumulated_ranks=stats["cumulatedRanks"],
                    crashes=stats["crashes"],
                    nruns=stats["numberOfRuns"],
                )
                for player_id, stats in data["playersStats"].items()
            ],
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                Player.top1,
                Player.cumulated_ranks,
                Player.crashes,
                Player.nruns,
            ],
            set_=dict(
                top1=stmt.excluded.top1,
                cumucumulated_ranks=stmt.excluded.cumucumulated_ranks,
                crashes=stmt.excluded.crashes,
                nruns=stmt.excluded.nruns,
            ),
        )
        s.execute(stmt)
        stmt = sqlite_upsert(PlayerRecord).values(
            [
                dict(
                    compention_id=compention_id,
                    player_id=player_id,
                    map_id=map_id,
                    time=lap_time,
                )
                for player_id, stats in data["playersStats"].items()
                for map_id, lap_time in stats["personalBests"].items()
            ],
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[PlayerRecord.time],
            set_=dict(time=stmt.excluded.time),
        )
        s.execute(stmt)
        stmt = sqlite_upsert(TournamentRecord).values(
            [
                dict(
                    compention_id=compention_id,
                    map_id=map_id,
                    player_id=record["webServicesUserId"],
                )
                for map_id, record in data["tournamentRecords"].items()
            ],
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[TournamentRecord.player_id],
            set_=dict(time=stmt.excluded.player_id),
        )
        s.execute(stmt)


def fetch_stats(
    compention_id: str,
    maps: list[str],
    players: list[str],
) -> TournamentStats:
    with session.begin() as s:
        player_stats: dict[str, PlayerStats] = {}
        for row in s.execute(
            select(Player, PlayerRecord).where(
                Player.player_id == PlayerRecord.player_id,
                Player.competition_id == PlayerRecord.competition_id,
                Player.competition_id == compention_id,
                Player.player_id.in_(players),
                PlayerRecord.map_id.in_(maps),
            ),
        ).all():
            player, record = row.tuple()
            if player.player_id in player_stats:
                player_stats[player.player_id]["personalBests"][
                    record.map_id
                ] = record.time
            else:
                player_stats[player.player_id] = {
                    "top1": player.top1,
                    "cumulatedRanks": player.cumulated_ranks,
                    "numberOfRuns": player.nruns,
                    "crashes": player.crashes,
                    "personalBests": {record.map_id: record.time},
                }
        tournament_records = s.execute(
            select(TournamentRecord.map_id, PlayerRecord.time).where(
                TournamentRecord.player_id == PlayerRecord.player_id,
                TournamentRecord.competition_id == PlayerRecord.competition_id,
                Player.competition_id == compention_id,
                TournamentRecord.map_id.in_(maps),
            ),
        ).all()
        return {
            "competitionUid": compention_id,
            "playersStats": player_stats,
            "tournamentRecords": {
                row.map_id: {
                    "time": row.time,
                    "webServicesUserId": row.player_id,
                }
                for row in tournament_records
            },
        }
