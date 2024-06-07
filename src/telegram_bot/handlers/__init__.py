from uuid import UUID

from aiogram import Router
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from services.user import UserService, UserData
from services.game import GameService, GameData

from telegram_bot.states import GameInteractions


router = Router()


class GameCallbackData(CallbackData, prefix="game"):
    game_id: UUID


@router.message(Command("my_games"))
async def my_games(message: Message, user_service: UserService, user_data: UserData) -> None:
    games = await user_service.get_all_user_games(user_data.id)
    buttons = [
        [InlineKeyboardButton(
            text=f"{game.name} ({game.created_at})",
            callback_data=GameCallbackData(
                game_id=game.game_id
            ).pack(),
        )] for game in games
    ]
    await message.reply("Your games:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@router.callback_query(StateFilter(None), GameCallbackData.filter())
async def game_selected(callback: CallbackQuery, state: FSMContext, callback_data: GameCallbackData, game_service: GameService) -> None:
    game_data = await game_service.get_game_data(callback_data.game_id)
    await state.update_data(game_id=callback_data.game_id)
    await callback.message.reply(f"You've selected game {game_data.game_id}, players are {game_data.users_in_game}, created at {game_data.created_at}, status is {game_data.status}")
    await callback.answer()
    await state.set_state(GameInteractions.interacting_with_game)
