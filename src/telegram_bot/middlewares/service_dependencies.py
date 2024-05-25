from typing import Callable, Dict, Awaitable, Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import TelegramObject, User

from services.user.base_implementation import UserServiceImplementation
from services.game.base_implementation import GameServiceImplementation


class UserServiceDependencyMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.user_service = UserServiceImplementation()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        data["user_service"] = self.user_service
        return await handler(event, data)


class GameServiceDependencyMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.game_service = GameServiceImplementation()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        data["game_service"] = self.game_service
        return await handler(event, data)
