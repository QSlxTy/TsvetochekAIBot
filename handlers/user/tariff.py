from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery

from keyboards.user.user_keyboard import back_menu_kb
from utils.all_text import tariff_info


async def get_tariff(call: CallbackQuery):
    await call.message.answer(tariff_info,
                              reply_markup=await back_menu_kb())


def register_handler(dp: Dispatcher):
    dp.callback_query.register(get_tariff, F.data == 'tariffs')
