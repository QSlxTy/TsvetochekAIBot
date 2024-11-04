from aiogram import Dispatcher, F
from aiogram.types import CallbackQuery

from keyboards.user.user_keyboard import support_kb, back_support_kb
from utils.all_text import support_how_it_works, support_admin, support_main_text


async def get_help(call: CallbackQuery):
    await call.message.answer(text=support_main_text,
                              reply_markup=await support_kb())


async def help_how_work(call: CallbackQuery):

    await call.message.answer(text=support_how_it_works,
                              reply_markup=await back_support_kb())


async def help_feedback(call: CallbackQuery):
    await call.message.answer(text=support_admin,
                              reply_markup=await back_support_kb())


def register_handler(dp: Dispatcher):
    dp.callback_query.register(get_help, F.data == 'support')
    dp.callback_query.register(help_how_work, F.data == 'how_work')
    dp.callback_query.register(help_feedback, F.data == 'feedback')
