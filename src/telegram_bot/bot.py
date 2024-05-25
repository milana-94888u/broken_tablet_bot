import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.utils.deep_linking import create_start_link

from services.user import UserService, UserData
from services.game import GameService, GameData

from telegram_bot.config import settings
from telegram_bot.middlewares.service_dependencies import UserServiceDependencyMiddleware, GameServiceDependencyMiddleware
from telegram_bot.middlewares.user_registration import RegistrationMiddleware


dp = Dispatcher()
bot = Bot(settings.api_token)


@dp.message(Command("create_game"))
async def create_game(message: Message, game_service: GameService, user_data: UserData) -> None:
    game_data = await game_service.create_game("test", user_data.id)
    print(game_data)


@dp.message(Command("my_games"))
async def my_games(message: Message, user_service: UserService, user_data: UserData) -> None:
    games = await user_service.get_all_user_games(user_data.id)
    buttons = [
        [InlineKeyboardButton(
            text=f"{game.name} ({game.created_at})", callback_data=str(game.game_id)
        )] for game in games
    ]
    await message.reply("Your games:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


async def change_game_context() -> None:
    pass


@dp.message(CommandStart(deep_link=True))
async def start_handler(message: Message, command: CommandObject, user_data: UserData) -> None:
    args = command.args
    await message.reply(f"Your payload is {args}, your id is {user_data.id}")


async def main() -> None:
    print(await create_start_link(bot, "game"))
    dp.message.middleware(UserServiceDependencyMiddleware())
    dp.message.middleware(GameServiceDependencyMiddleware())
    dp.message.middleware(RegistrationMiddleware())
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
