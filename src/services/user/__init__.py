from abc import ABC, abstractmethod
from uuid import UUID

from services.game.schemas import GameData

from .schemas import UserData


class UserService(ABC):
    @abstractmethod
    async def get_or_register_telegram_user(self, telegram_user_id: int) -> UserData:
        raise NotImplementedError

    @abstractmethod
    async def get_all_user_games(self, user_id: UUID) -> list[GameData]:
        raise NotImplementedError
