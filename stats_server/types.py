from __future__ import annotations

from typing import TypedDict


class TournamentRecord(TypedDict):
    webServicesUserId: str
    time: int


class PlayerStats(TypedDict):
    top1: int
    cumulatedRanks: int
    crashes: int
    numberOfRuns: int
    personalBests: dict[str, int]


class TournamentStats(TypedDict):
    competitionUid: str
    tournamentRecords: dict[str, TournamentRecord]
    playersStats: dict[str, PlayerStats]
