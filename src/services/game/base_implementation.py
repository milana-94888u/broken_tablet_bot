from uuid import UUID
from random import shuffle
from datetime import datetime, UTC
from typing import Self

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from db import session_factory
from models import Game, UserInGame, GameStatus
from utils.photo_utils import create_blurred_image

from . import GameService, GameData
from services.user_notification import UserNotificationService
from services.artwork_storage import ArtworkStorageService
from services.user import UserData


class GameServiceImplementation(GameService):
    async def finish_game(self, game_id: UUID) -> None:
        pass

    async def process_completed_task(
        self, game_id: UUID, user_id: UUID, *artwork_args
    ) -> None:
        async with session_factory() as session:
            statement = (
                select(Game)
                .filter_by(game_id=game_id)
                .options(joinedload(Game.users_in_game))
                .options(joinedload(Game.users))
            )
            result = await session.scalars(statement)
            game = result.unique().one_or_none()

            if game.status != GameStatus.ACTIVE:
                raise ValueError("The game is not active")

            if 0 <= game.current_turn < len(game.users_in_game):
                if game.users_in_game[game.current_turn].user_id != user_id:
                    raise ValueError("Incorrect user id passed")
                artwork_path = f"artworks/{game_id}/{user_id}.jpeg"
                await self.artwork_storage_service.store_artwork(
                    *artwork_args, destination=artwork_path
                )
                current_user: UserInGame = game.users_in_game[game.current_turn]
                current_user.path_to_artwork = artwork_path
                current_user.task_completed_at = datetime.now(UTC)
                await session.commit()
            else:
                raise Exception("Error processing game turn")
        blurred_artwork_path = create_blurred_image(artwork_path)
        await self.proceed_next_turn(game_id, blurred_artwork_path)

    async def process_acknowledged_task(self, game_id: UUID, user_id: UUID) -> None:
        async with session_factory() as session:
            statement = (
                select(Game)
                .filter_by(game_id=game_id)
                .options(joinedload(Game.users_in_game))
                .options(joinedload(Game.users))
            )
            result = await session.scalars(statement)
            game = result.unique().one_or_none()

            if game.status != GameStatus.ACTIVE:
                raise ValueError("The game is not active")

            if 0 <= game.current_turn < len(game.users_in_game):
                if game.users_in_game[game.current_turn].user_id != user_id:
                    raise ValueError("Incorrect user id passed")
                current_user: UserInGame = game.users_in_game[game.current_turn]
                current_user.task_received_at = datetime.now(UTC)
                await session.commit()
            else:
                raise Exception("Error processing game turn")

    def __init__(
        self,
        notification_service: UserNotificationService,
        artwork_storage_service: ArtworkStorageService,
    ) -> None:
        self.artwork_storage_service = artwork_storage_service
        self.notification_service = notification_service

    async def get_current_player(self, game_id: UUID) -> UserData:
        async with session_factory() as session:
            statement = (
                select(Game)
                .filter_by(game_id=game_id)
                .options(joinedload(Game.users_in_game))
                .options(joinedload(Game.users))
            )
            result = await session.scalars(statement)
            game = result.unique().one_or_none()

            if game.status != GameStatus.ACTIVE:
                raise ValueError("The game is not active")

            if 0 <= game.current_turn < len(game.users_in_game):
                return UserData.model_validate(
                    game.users_in_game[game.current_turn].user
                )
            raise Exception("Error processing game turn")

    async def proceed_next_turn(
        self, game_id: UUID, prev_artwork_path: str | None = None
    ) -> None:
        async with session_factory() as session:
            statement = (
                select(Game)
                .filter_by(game_id=game_id)
                .options(joinedload(Game.users_in_game))
                .options(joinedload(Game.users))
            )
            result = await session.scalars(statement)
            game = result.unique().one_or_none()

            if game.current_turn < 0:  # first turn
                game.current_turn = 0
                user_in_game: UserInGame = game.users_in_game[game.current_turn]
                user_in_game.task_provided_at = datetime.now(UTC)
                current_user = UserData.model_validate(
                    game.users_in_game[game.current_turn].user
                )
                await self.notification_service.notify_next_player(
                    GameData.model_validate(game), current_user, prev_artwork_path
                )
            elif game.current_turn < len(game.users_in_game) - 1:  # not last turn
                game.current_turn += 1
                user_in_game: UserInGame = game.users_in_game[game.current_turn]
                user_in_game.task_provided_at = datetime.now(UTC)
                current_user = UserData.model_validate(
                    game.users_in_game[game.current_turn].user
                )
                await self.notification_service.notify_next_player(
                    GameData.model_validate(game), current_user, prev_artwork_path
                )
            else:  # game finished
                game.status = GameStatus.FINISHED
                await self.notification_service.notify_game_finished(
                    GameData.model_validate(game)
                )
            await session.commit()

    async def get_game_data(self, game_id: UUID) -> GameData:
        async with session_factory() as session:
            statement = (
                select(Game)
                .filter_by(game_id=game_id)
                .options(joinedload(Game.users_in_game))
                .options(joinedload(Game.users))
            )
            result = await session.scalars(statement)
            game = result.unique().one_or_none()

            return GameData.model_validate(game)

    async def start_game(self, game_id: UUID, user_id: UUID) -> GameData:
        async with session_factory() as session:
            statement = (
                select(Game)
                .filter_by(game_id=game_id)
                .options(joinedload(Game.users_in_game))
                .options(joinedload(Game.users))
            )
            result = await session.scalars(statement)
            game = result.unique().one_or_none()
            game.status = GameStatus.ACTIVE
            users_in_game = list(game.users_in_game)
            shuffle(users_in_game)
            for turn_number, user_in_game in enumerate(users_in_game):
                user_in_game: UserInGame
                user_in_game.turn_number = turn_number
            await session.commit()

            game_data = GameData.model_validate(game)

        await self.proceed_next_turn(game_id)

        return game_data

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
            user_in_game = UserInGame(
                game_id=game_id, user_id=user_id, permissions={"user": True}
            )
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

            return await self.get_game_data(game.game_id)
