from aiogram import Router, F
from aiogram.types import Message
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from services.game import GameService
from services.user import UserData

from telegram_bot.states import GameInteractions


router = Router()


@router.message(
    GameInteractions.waiting_for_artwork, F.content_type == ContentType.PHOTO
)
async def artwork_sent(
    message: Message, state: FSMContext, game_service: GameService, user_data: UserData
) -> None:
    data = await state.get_data()
    biggest_photo_size = max(message.photo, key=lambda photo_size: photo_size.file_size)
    await game_service.process_completed_task(
        data["game_id"], user_data.user_id, biggest_photo_size.file_id
    )
