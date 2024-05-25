from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


from services.user.schemas import UserData


class GameData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    game_id: UUID
    name: str
    created_at: datetime


class UserInGameData(BaseModel):
    user: UserData
    game: GameData
