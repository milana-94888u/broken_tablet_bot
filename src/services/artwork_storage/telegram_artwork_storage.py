import os
from typing import Callable, Awaitable

from . import ArtworkStorageService


class TelegramArtworkStorageService(ArtworkStorageService):
    def __init__(
        self, telegram_file_downloader: Callable[[str, str], Awaitable]
    ) -> None:
        self.telegram_file_downloader = telegram_file_downloader

    async def store_artwork(self, *args, destination: str) -> None:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        await self.telegram_file_downloader(args[0], destination)
