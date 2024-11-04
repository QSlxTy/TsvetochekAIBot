from datetime import datetime

from sqlalchemy import select, BigInteger, update, Integer, BOOLEAN, Text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker, Mapped, mapped_column

from ..modeles import AbstractModel


class User(AbstractModel):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger(), unique=True)
    username: Mapped[str] = mapped_column(Text, default=None)
    fullname: Mapped[str] = mapped_column(Text, default=None)
    reg_time: Mapped[datetime] = mapped_column(default=datetime.now())
    phone: Mapped[str] = mapped_column(Text, default='Не указан')
    first_answer: Mapped[int] = mapped_column(Integer(), default=0)
    second_answer: Mapped[int] = mapped_column(Integer(), default=0)
    third_answer: Mapped[int] = mapped_column(Integer(), default=0)
    is_admin: Mapped[str] = mapped_column(BOOLEAN, default=0)


async def get_user(select_by: dict, session_maker: sessionmaker) -> User:
    """
    Получить User
    :param select_by:
    :param session_maker:
    :return:
    """
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(
                select(User).filter_by(**select_by)
            )
            return result.scalars().one()


async def create_user(user_id: int, username: str, full_name: str, session_maker: sessionmaker) -> [User, Exception]:
    async with session_maker() as session:
        async with session.begin():
            user = User(
                user_id=user_id,
                username=username,
                fullname=full_name
            )
            try:
                session.add(user)
                return User
            except ProgrammingError as _e:
                return _e


async def is_user_exists(user_id: int, session_maker: sessionmaker) -> bool:
    async with session_maker() as session:
        async with session.begin():
            sql_res = await session.execute(select(User).where(User.user_id == user_id))
            return bool(sql_res.first())


async def update_user(telegram_id: int, data: dict, session_maker: sessionmaker) -> None:
    async with session_maker() as session:
        async with session.begin():
            await session.execute(update(User).where(User.user_id == telegram_id).values(data))
            await session.commit()


async def get_users(session_maker: sessionmaker) -> User:
    async with session_maker() as session:
        async with session.begin():
            result = await session.execute(select(User))
            return result.scalars().all()
