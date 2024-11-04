from aiogram import Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker

from integrations.database.models.photos import get_photo
from keyboards.user.user_keyboard import back_menu_kb
from utils.all_text import none_create_colors


async def get_my_colors(call: CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    try:
        my_color = await get_photo({'user_id': call.from_user.id}, session_maker)
        await call.bot.send_photo(photo=my_color.result_url,
                                  chat_id=call.from_user.id)
        await call.bot.send_message(chat_id=call.from_user.id,
                                    text=my_color.recommendation,
                                    reply_markup=await back_menu_kb())
    except NoResultFound:
        await call.message.answer(
            text=none_create_colors,
            reply_markup=await back_menu_kb())


def register_handler(dp: Dispatcher):
    dp.callback_query.register(get_my_colors, F.data.startswith('my_colors'))
