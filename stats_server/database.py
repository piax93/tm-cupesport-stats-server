from __future__ import annotations

import os
import tempfile

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import sessionmaker


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = "players"

    competition_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    player_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    top1: Mapped[int] = mapped_column(nullable=False)
    cumulated_ranks: Mapped[int] = mapped_column(nullable=False)
    crashes: Mapped[int] = mapped_column(nullable=False)
    nruns: Mapped[int] = mapped_column(nullable=False)


class PlayerRecord(Base):
    __tablename__ = "player_records"

    competition_id: Mapped[str] = mapped_column(
        ForeignKey("players.competition_id"),
        primary_key=True,
    )
    player_id: Mapped[str] = mapped_column(
        ForeignKey("players.player_id"),
        primary_key=True,
    )
    map_id: Mapped[str] = mapped_column(String(48), primary_key=True)
    time: Mapped[int] = mapped_column(nullable=False)


class TournamentRecord(Base):
    __tablename__ = "tournament_records"

    competition_id: Mapped[str] = mapped_column(
        ForeignKey("player_records.competition_id"),
        primary_key=True,
    )
    map_id: Mapped[str] = mapped_column(
        ForeignKey("player_records.map_id"),
        primary_key=True,
    )
    player_id: Mapped[str] = mapped_column(ForeignKey("player_records.player_id"))


engine = create_engine(
    f"sqlite:///{os.path.join(tempfile.gettempdir(), 'cupesport_stats.sqlite')}",
)
session = sessionmaker(engine)

try:
    Base.metadata.create_all(engine)
except OperationalError as e:
    if "already exists" not in str(e):
        raise
