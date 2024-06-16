from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db import session_factory
from models import User, Game, UserInGame

from . import UserService, UserData
from ..game import GameData


class UserServiceImplementation(UserService):
    async def get_or_register_telegram_user(self, telegram_user_id: int) -> UserData:
        async with session_factory() as session:
            statement = select(User).filter_by(telegram_user_id=telegram_user_id)
            result = await session.scalars(statement)
            if user := result.one_or_none():
                return UserData.model_validate(user)
            user = User(telegram_user_id=telegram_user_id)
            session.add(user)
            await session.commit()
            return UserData.model_validate(user)

    async def get_all_user_games(self, user_id: UUID) -> list[GameData]:
        async with session_factory() as session:
            statement = (
                select(User).filter_by(user_id=user_id).options(joinedload(User.games).joinedload(Game.users_in_game)).options(joinedload(User.games).joinedload(Game.users))
            )
            result = await session.scalars(statement)
            user = result.unique().one_or_none()
            if not user:
                raise Exception("User not found")
            return [GameData.model_validate(game) for game in user.games]
