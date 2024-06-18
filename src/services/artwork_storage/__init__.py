from abc import ABC, abstractmethod
from uuid import UUID

from services.game.schemas import GameData


class ArtworkStorageService(ABC):
    @abstractmethod
    async def store_artwork(self, *args, destination: str) -> None:
        raise NotImplementedError
