from aiogram.filters.callback_data import CallbackData

from services.game.schemas import GameData


class GameCallbackData(CallbackData, GameData):
    pass
