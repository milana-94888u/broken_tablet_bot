from aiogram import Router
from aiogram.types import Message

from telegram_bot.states import GameInteractions


router = Router()


@router.message(GameInteractions.waiting_for_artwork)
async def artwork_sent(message: Message) -> None:
    pass
