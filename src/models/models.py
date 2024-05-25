from datetime import datetime, timezone
from typing import Annotated, Any
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base


class GameStatus(Enum):
    PENDING = 1
    ACTIVE = 2
    FINISHED = 3
    CANCELED = 4


def str_with_length(length: int) -> type[Annotated]:
    return Annotated[str, mapped_column(String(length))]


class User(Base):
    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    telegram_user_id: Mapped[Annotated[int, mapped_column(index=True)]]

    games: Mapped[list["Game"]] = relationship(secondary=lambda: UserInGame.__table__, back_populates="users")
    game_registrations: Mapped[list["UserInGame"]] = relationship(back_populates="user")


class Game(Base):
    game_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str_with_length(50)] = mapped_column(nullable=True)
    max_players: Mapped[int] = mapped_column(default=8)
    status: Mapped[GameStatus] = mapped_column(default=GameStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    current_turn: Mapped[int] = mapped_column(default=-1)

    users: Mapped[list["User"]] = relationship(secondary=lambda: UserInGame.__table__, back_populates="games")
    users_in_game: Mapped[list["UserInGame"]] = relationship(back_populates="game")


class UserInGame(Base):
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.user_id), primary_key=True)
    game_id: Mapped[UUID] = mapped_column(ForeignKey(Game.game_id), primary_key=True)
    permissions: Mapped[dict[str, Any]]
    turn_number: Mapped[int] = mapped_column(default=-1)
    task_provided_at: Mapped[datetime] = mapped_column(nullable=True)
    task_received_at: Mapped[datetime] = mapped_column(nullable=True)
    task_completed_at: Mapped[datetime] = mapped_column(nullable=True)

    game: Mapped["Game"] = relationship(back_populates="users_in_game")
    user: Mapped["User"] = relationship(back_populates="game_registrations")
