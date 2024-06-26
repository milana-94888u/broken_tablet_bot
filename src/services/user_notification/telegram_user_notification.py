from typing import Callable

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BufferedInputFile,
    MessageEntity,
    User,
)

from telegram_bot.handlers import TaskAcceptData
from telegram_bot.states import GameInteractions

from . import UserNotificationService
from ..game import GameData
from ..user import UserData


class TelegramUserNotificationService(UserNotificationService):
    def __init__(
        self, bot: Bot, user_fsm_context_receiver: Callable[[int], FSMContext]
    ) -> None:
        self.bot = bot
        self.user_fsm_context_receiver = user_fsm_context_receiver

    async def notify_game_started(self, game_data: GameData) -> None:
        for user_in_game in game_data.users_in_game:
            await self.bot.send_message(
                user_in_game.user.telegram_user_id, "The game has started"
            )

    async def notify_next_player(
        self,
        game_data: GameData,
        user_data: UserData,
        prev_artwork_path: str | None = None,
    ) -> None:
        for user_in_game in game_data.users_in_game:
            if user_in_game.user.user_id != user_data.user_id:
                await self.bot.send_message(
                    user_in_game.user.telegram_user_id,
                    f"This Player's turn now. Waiting for accept",
                    entities=[
                        MessageEntity(
                            type="text_mention",
                            offset=0,
                            length=13,
                            user=User(
                                id=user_data.telegram_user_id,
                                is_bot=False,
                                first_name="",
                            ),
                        )
                    ],
                )
        buttons = [
            [
                InlineKeyboardButton(
                    text=f"Accept task",
                    callback_data=TaskAcceptData(game_id=game_data.game_id).pack(),
                )
            ]
        ]
        if prev_artwork_path:
            await self.bot.send_photo(
                user_data.telegram_user_id,
                BufferedInputFile.from_file(prev_artwork_path),
                caption="Your turn now, try to draw something above the blurred image",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            )
        else:
            await self.bot.send_message(
                user_data.telegram_user_id,
                f"Your turn now. It's the first turn, just draw anything you want",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
            )
        state = self.user_fsm_context_receiver(user_data.telegram_user_id)
        await state.set_state(GameInteractions.waiting_for_task_acknowledge)

    async def notify_game_finished(self, game_data: GameData) -> None:
        pass
