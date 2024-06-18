from typing import Callable, Dict, Awaitable, Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram import Bot
from aiogram.types import TelegramObject, User
from aiogram.fsm.context import FSMContext

from services.user.base_implementation import UserServiceImplementation
from services.game.base_implementation import GameServiceImplementation
from services.user_notification.telegram_user_notification import (
    TelegramUserNotificationService,
)
from services.artwork_storage.telegram_artwork_storage import (
    TelegramArtworkStorageService,
)


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
    def __init__(
        self,
        bot: Bot,
        user_fsm_context_receiver: Callable[[int], FSMContext],
        telegram_file_downloader: Callable[[str, str], Awaitable],
    ) -> None:
        self.game_service = GameServiceImplementation(
            TelegramUserNotificationService(bot, user_fsm_context_receiver),
            TelegramArtworkStorageService(telegram_file_downloader),
        )

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        print(data)
        data["game_service"] = self.game_service
        return await handler(event, data)
