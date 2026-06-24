from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

from stats_server.database import Player
from stats_server.database import PlayerRecord
from stats_server.database import TournamentRecord
from stats_server.database import session
from stats_server.types import PlayerStats
from stats_server.types import TournamentStats


def update_stats(competition_id: str, data: TournamentStats) -> None:
    competition_id = competition_id or data["competitionUid"]
    with session.begin() as s:
        stmt = sqlite_upsert(Player).values(
            [
                dict(
                    competition_id=competition_id,
                    player_id=player_id,
                    top1=stats["top1"],
                    cumulated_ranks=stats["cumulatedRanks"],
                    crashes=stats["crashes"],
                    nruns=stats["numberOfRuns"],
                )
                for player_id, stats in data["playersStats"].items()
            ],
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                Player.competition_id,
                Player.player_id,
            ],
            set_=dict(
                top1=stmt.excluded.top1,
                cumulated_ranks=stmt.excluded.cumulated_ranks,
                crashes=stmt.excluded.crashes,
                nruns=stmt.excluded.nruns,
            ),
        )
        s.execute(stmt)
        stmt = sqlite_upsert(PlayerRecord).values(
            [
                dict(
                    competition_id=competition_id,
                    player_id=player_id,
                    map_id=map_id,
                    time=lap_time,
                )
                for player_id, stats in data["playersStats"].items()
                for map_id, lap_time in stats["personalBests"].items()
            ],
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                PlayerRecord.competition_id,
                PlayerRecord.player_id,
                PlayerRecord.map_id,
            ],
            set_=dict(time=stmt.excluded.time),
        )
        s.execute(stmt)
        stmt = sqlite_upsert(TournamentRecord).values(
            [
                dict(
                    competition_id=competition_id,
                    map_id=map_id,
                    player_id=record["webServicesUserId"],
                )
                for map_id, record in data["tournamentRecords"].items()
            ],
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                TournamentRecord.competition_id,
                TournamentRecord.map_id,
            ],
            set_=dict(player_id=stmt.excluded.player_id),
        )
        s.execute(stmt)


def fetch_stats(
    competition_id: str,
    maps: list[str],
    players: list[str],
) -> TournamentStats:
    with session.begin() as s:
        player_stats: dict[str, PlayerStats] = {}
        for row in s.execute(
            select(Player, PlayerRecord)
            .join(
                PlayerRecord,
                Player.player_id == PlayerRecord.player_id
                and Player.competition_id == PlayerRecord.competition_id,
            )
            .where(
                Player.competition_id == competition_id,
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
            select(
                TournamentRecord.map_id,
                TournamentRecord.player_id,
                PlayerRecord.time,
            )
            .join(
                PlayerRecord,
                TournamentRecord.player_id == PlayerRecord.player_id
                and TournamentRecord.competition_id == PlayerRecord.competition_id,
            )
            .where(
                PlayerRecord.competition_id == competition_id,
                TournamentRecord.map_id.in_(maps),
            ),
        ).all()
        return {
            "competitionUid": competition_id,
            "playersStats": player_stats,
            "tournamentRecords": {
                row.map_id: {
                    "time": row.time,
                    "webServicesUserId": row.player_id,
                }
                for row in tournament_records
            },
        }
