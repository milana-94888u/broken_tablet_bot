from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models import GameStatus

from services.user.schemas import UserData


class UserInGameData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: UserData
    turn_number: int


class GameData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_id: UUID
    name: str
    created_at: datetime
    status: GameStatus

    users_in_game: list[UserInGameData]
