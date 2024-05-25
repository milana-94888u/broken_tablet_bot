import asyncio

from sqlalchemy.ext.asyncio import AsyncConnection

from models import *
from models.base import Base

from .engine import engine, session_factory


__all__ = ["session_factory"]


async def create_models() -> None:
    async with engine.begin() as connection:
        connection: AsyncConnection
        await connection.run_sync(Base.metadata.create_all)


asyncio.run(create_models())
