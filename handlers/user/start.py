from aiogram import types, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from integrations.database.models.photos import get_photos
from integrations.database.models.user import is_user_exists, create_user
from keyboards.user.user_keyboard import get_phone_kb, menu_kb
from src.config import conf
from utils.all_text import menu, hello
from utils.notify import create_reg_notify


async def start_command(message: types.Message, session_maker: sessionmaker):
    if not await is_user_exists(message.from_user.id, session_maker):
        await create_user(user_id=message.from_user.id,
                          username=message.from_user.username,
                          full_name=message.from_user.full_name,
                          session_maker=session_maker)
        await message.answer(text=hello,
                             reply_markup=await get_phone_kb(),
                             disable_notification=True)
        await create_reg_notify(message.from_user.id)
    else:
        await message.answer_photo(photo=conf.logo_id,
                                   caption=menu,
                                   reply_markup=await menu_kb())


async def main_menu(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    photos = await get_photos({'user_id': call.from_user.id}, session_maker)

    if not await is_user_exists(call.from_user.id, session_maker):
        await create_user(user_id=call.from_user.id,
                          username=call.from_user.username,
                          full_name=call.from_user.full_name,
                          session_maker=session_maker)
        await call.message.answer(text=hello,
                                  reply_markup=await get_phone_kb(),
                                  disable_notification=True)
    else:

        await call.message.answer_photo(photo=conf.logo_id,
                                        caption=menu,
                                        reply_markup=await menu_kb())

    await state.update_data(photos=photos)


def register_start_handler(dp: Dispatcher):
    dp.message.register(start_command, Command('start'))
    dp.callback_query.register(main_menu, F.data == 'main_menu')
