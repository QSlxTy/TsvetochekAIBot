from datetime import datetime

from sqlalchemy import select, BigInteger, Text, update
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column

from ..modeles import AbstractModel


class Photo(AbstractModel):
    __tablename__ = 'photos'
    photo_url: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(BigInteger(), unique=True)
    result_url: Mapped[str] = mapped_column(Text)
    result_json: Mapped[str] = mapped_column(Text)
    recommendation: Mapped[str] = mapped_column(Text)
    create_time: Mapped[datetime] = mapped_column(default=datetime.now())


async def get_photo(select_by: dict, session_maker: sessionmaker) -> Photo:
    """
    Получить User
    :param select_by:
    :param session_maker:
    :return:
    """
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(Photo).filter_by(**select_by)
            )
            return result.scalars().one()


async def create_photo(photo_url: str, user_id: int, result_url: str, recommendation: str, result_json: str,
                       session_maker: sessionmaker) -> [Photo,
                                                        Exception]:
    async with session_maker() as session:
        async with session.begin():
            photo = Photo(photo_url=photo_url,
                          user_id=user_id,
                          result_url=result_url,
                          recommendation=recommendation,
                          result_json=result_json
                          )
            try:
                session.add(photo)
                return Photo
            except ProgrammingError as _e:
                return _e


async def get_photos(select_by: dict, session_maker: sessionmaker) -> Photo:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(Photo).filter_by(**select_by)
            )
            return result.scalars().all()


async def update_photo_info(telegram_id: int, data: dict, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            await session.execute(update(Photo).where(Photo.user_id == telegram_id).values(data))
            await session.commit()


async def is_photo_exists(user_id: int, session_maker: sessionmaker) -> bool:
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(Photo).where(Photo.user_id == user_id))
            return bool(sql_res.first())
