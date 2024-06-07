from abc import ABC, abstractmethod
from uuid import UUID

from .schemas import GameData


class GameService(ABC):
    @abstractmethod
    async def create_game(self, name: str, user_id: UUID) -> GameData:
        raise NotImplementedError

    @abstractmethod
    async def register_user_to_game(self, game_id: UUID, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_possible_actions_for_user(self, game_id: UUID, user_id: UUID) -> list:
        raise NotImplementedError

    @abstractmethod
    async def start_game(self, game_id: UUID, user_id: UUID) -> GameData:
        raise NotImplementedError

    @abstractmethod
    async def get_game_data(self, game_id: UUID) -> GameData:
        raise NotImplementedError
