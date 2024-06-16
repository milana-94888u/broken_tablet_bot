import asyncio
from uuid import UUID

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.deep_linking import create_start_link
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from services.user import UserService, UserData
from services.game import GameService, GameData

from telegram_bot.config import settings
from telegram_bot.middlewares.service_dependencies import (
    UserServiceDependencyMiddleware,
    GameServiceDependencyMiddleware,
)
from telegram_bot.middlewares.user_registration import RegistrationMiddleware
from telegram_bot.handlers import router
from telegram_bot.states import GameInteractions


dp = Dispatcher()
bot = Bot(settings.api_token)


@dp.message(Command("create_game"))
async def create_game(
    message: Message, game_service: GameService, user_data: UserData
) -> None:
    game_data = await game_service.create_game("test", user_data.user_id)
    await message.reply(
        f"The game {game_data.name} is created at {game_data.created_at}"
        f"\nJoin link is {await create_start_link(bot, str(game_data.game_id))}"
    )


@dp.message(GameInteractions.interacting_with_game, Command("start_game"))
async def start_game(
    message: Message, state: FSMContext, game_service: GameService, user_data: UserData
) -> None:
    state_data = await state.get_data()
    game_id = state_data["game_id"]
    game_data = await game_service.start_game(game_id, user_data.user_id)
    await message.reply(
        f"You've started the game {game_data.game_id}, players are {game_data.users_in_game}, created at {game_data.created_at}, status is {game_data.status}"
    )


async def change_game_context() -> None:
    pass


@dp.message(CommandStart(deep_link=True))
async def new_user_handler(
    message: Message,
    command: CommandObject,
    game_service: GameService,
    user_data: UserData,
) -> None:
    args = command.args
    await game_service.register_user_to_game(
        game_id=UUID(args), user_id=user_data.user_id
    )
    await message.reply(f"You've been registered to the game!")


def get_user_fsm_context(telegram_user_id: int) -> FSMContext:
    return FSMContext(
        storage=dp.storage,
        key=StorageKey(
            bot_id=bot.id, chat_id=telegram_user_id, user_id=telegram_user_id
        ),
    )


async def main() -> None:
    print(await create_start_link(bot, "game"))
    dp.include_router(router)
    dp.update.middleware(UserServiceDependencyMiddleware())
    dp.update.middleware(GameServiceDependencyMiddleware(bot, get_user_fsm_context))
    dp.update.middleware(RegistrationMiddleware())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
