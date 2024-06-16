from abc import ABC, abstractmethod

from services.game.schemas import GameData
from services.user.schemas import UserData


class UserNotificationService(ABC):
    @abstractmethod
    async def notify_game_started(self, game_data: GameData) -> None:
        raise NotImplementedError

    @abstractmethod
    async def notify_next_player(
        self, game_data: GameData, user_data: UserData
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def notify_game_finished(self, game_data: GameData) -> None:
        raise NotImplementedError
