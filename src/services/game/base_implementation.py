from uuid import UUID
from random import shuffle

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db import session_factory
from models import Game, UserInGame, GameStatus

from . import GameService, GameData


class GameServiceImplementation(GameService):
    async def get_game_data(self, game_id: UUID) -> GameData:
        async with session_factory() as session:
            statement = select(Game).filter_by(game_id=game_id).options(joinedload(Game.users_in_game)).options(joinedload(Game.users))
            result = await session.scalars(statement)
            game = result.unique().one_or_none()

            return GameData.model_validate(game)

    async def start_game(self, game_id: UUID, user_id: UUID) -> GameData:
        async with session_factory() as session:
            statement = select(Game).filter_by(game_id=game_id).options(joinedload(Game.users_in_game)).options(joinedload(Game.users))
            result = await session.scalars(statement)
            game = result.unique().one_or_none()
            game.status = GameStatus.ACTIVE
            users_in_game = list(game.users_in_game)
            shuffle(users_in_game)
            for turn_number, user_in_game in enumerate(users_in_game):
                user_in_game: UserInGame
                user_in_game.turn_number = turn_number
            await session.commit()

            return GameData.model_validate(game)

    async def get_possible_actions_for_user(self, game_id: UUID, user_id: UUID) -> list:
        async with session_factory() as session:
            statement = select(UserInGame).filter_by(game_id=game_id, user_id=user_id)
            result = await session.scalars(statement)
            user_in_game = result.one_or_none()
            return list(user_in_game.permissions)

    async def register_user_to_game(self, game_id: UUID, user_id: UUID) -> None:
        async with session_factory() as session:
            statement = select(UserInGame).filter_by(game_id=game_id, user_id=user_id)
            result = await session.scalars(statement)
            user_in_game = result.one_or_none()
            if user_in_game:
                raise Exception("User already registered")
            user_in_game = UserInGame(game_id=game_id, user_id=user_id, permissions={"user": True})
            session.add(user_in_game)
            await session.commit()

    async def create_game(self, name: str, user_id: UUID) -> GameData:
        async with session_factory() as session:
            game = Game(name=name)
            creator = UserInGame(
                user_id=user_id,
                permissions={"creator": True},
                game=game,
            )
            session.add_all([game, creator])
            await session.commit()

            return GameData.model_validate(game)
