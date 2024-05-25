from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
    AsyncSession,
)

from .config import settings


engine = create_async_engine(url=settings.url, echo=settings.echo)
session_factory = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
