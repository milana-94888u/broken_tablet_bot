from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserData(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    telegram_user_id: int
