from aiogram import types, F, Dispatcher
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from integrations.database.models.user import update_user
from keyboards.user.user_keyboard import get_poll_answers_kb
from utils.all_text import first_question, poll_answers
from utils.notify import create_reg_notify
from utils.states.user import FSMPhone


async def get_phone_number(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    await update_user(message.from_user.id, {'phone': int(message.contact.phone_number)}, session_maker)
    await state.set_state(FSMPhone.get_phone_number)
    await create_reg_notify(message.from_user.id)
    await message.answer(text=first_question, reply_markup=await get_poll_answers_kb(poll_answers=poll_answers[0]))



def register_handler(dp: Dispatcher):
    dp.message.register(get_phone_number, F.content_type == 'contact')
