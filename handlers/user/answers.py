from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from integrations.database.models.user import update_user
from keyboards.user.user_keyboard import get_poll_answers_kb
from utils.all_text import second_question_txt, third_question_txt, poll_answers
from utils.notify import create_reg_notify
from utils.states.user import FSMPhone, FSMAnswer


async def second_question(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    await state.set_state(FSMAnswer.second_answer)
    count_answer = 0
    for answer in poll_answers[0]:
        count_answer += 1
        if message.text in answer:
            await update_user(message.from_user.id, {'first_answer': count_answer}, session_maker)
            break
    await create_reg_notify(message.from_user.id)
    await message.answer(text=second_question_txt, reply_markup=await get_poll_answers_kb(poll_answers=poll_answers[1]))


async def third_question(message: types.Message, session_maker: sessionmaker, state: FSMContext):
    await state.set_state(FSMAnswer.third_answer)
    count_answer = 0
    for answer in poll_answers[1]:
        count_answer += 1
        if message.text in answer:
            await update_user(message.from_user.id, {'second_answer': count_answer}, session_maker)
            break
    await create_reg_notify(message.from_user.id)
    await message.answer(text=third_question_txt, reply_markup=await get_poll_answers_kb(poll_answers=poll_answers[2]))


def register_handler(dp: Dispatcher):
    dp.message.register(second_question, FSMPhone.get_phone_number)
    dp.message.register(third_question, FSMAnswer.second_answer)
