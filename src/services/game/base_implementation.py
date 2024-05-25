from uuid import UUID

from db import session_factory
from models import Game, UserInGame

from . import GameService, GameData


class GameServiceImplementation(GameService):
    async def start_game(self, game_id: UUID, user_id: UUID) -> None:
        pass

    async def get_possible_actions_for_user(self, game_id: UUID, user_id: UUID) -> list:
        pass

    async def register_user_to_game(self, game_id: UUID, user_id: UUID) -> None:
        pass

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
            return GameData(game)
