import os
import uuid
from datetime import datetime

from aiogram import Dispatcher, F, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import sessionmaker

from bot_start import bot
from integrations.database.models.photos import create_photo, is_photo_exists, update_photo_info, get_photos
from integrations.database.models.user import update_user
from keyboards.user.user_keyboard import back_menu_kb, go_kb
from utils import all_text
from utils.all_text import bot_vision_error
from utils.notify import remove_reg_notify
from utils.states.user import FSMAnswer, FSMPhoto
from utils.vision import upload_image_telegraph, json_load, delete_file


async def go_photo_from_answers(message: types.Message, state: FSMContext, session_maker: sessionmaker):
    await state.set_state(FSMPhoto.go_photo)
    count_answer = 0
    for answer in all_text.poll_answers[2]:
        count_answer += 1
        if message.text in answer:
            await update_user(message.from_user.id, {'third_answer': count_answer}, session_maker)
            break
    await remove_reg_notify(message.from_user.id)
    await message.answer(text=all_text.add_photo, reply_markup=await back_menu_kb())


async def go_photo(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(FSMPhoto.go_photo)
    await call.message.answer(text=all_text.add_photo, reply_markup=await back_menu_kb())


async def get_first_photo(message: types.Message, state: FSMContext):
    await message.answer(text=all_text.beautiful_girl, reply_markup=await go_kb())

    try:
        await bot.download(message.photo[-1],
                           destination=os.path.abspath(
                               f"files/photos/{message.from_user.id}/{message.photo[-1].file_id}.jpg"))
    except FileNotFoundError:
        os.makedirs(f'files/photos/{message.from_user.id}')
        await bot.download(message.photo[-1],
                           destination=os.path.abspath(
                               f"files/photos/{message.from_user.id}/{message.photo[-1].file_id}.jpg"))
    await state.update_data(photo_path=f"files/photos/{message.from_user.id}/{message.photo[-1].file_id}.jpg",
                            photo_id=str(uuid.uuid4()))


async def new_photo(call: types.CallbackQuery, state: FSMContext, session_maker: sessionmaker):
    data = await state.get_data()
    await call.message.answer(text='⏳')
    url, path = await upload_image_telegraph(data['photo_path'], data['photo_id'])
    try:
        await delete_file(path)
        recommendation, url_color, json_answer = await json_load(url, call.from_user.id)
        if 'error' in recommendation:
            await call.message.answer(bot_vision_error,
                                      reply_markup=await back_menu_kb())
        else:
            if not await is_photo_exists(call.from_user.id, session_maker):
                await create_photo(user_id=call.from_user.id,
                                   recommendation=recommendation,
                                   photo_url=url,
                                   result_url=url_color,
                                   result_json=json_answer,
                                   session_maker=session_maker)
            else:
                await update_photo_info(call.from_user.id, {'photo_url': url,
                                                            'result_url': url_color,
                                                            'create_time': datetime.now(),
                                                            'recommendation': recommendation}, session_maker)
            await call.message.answer(text=all_text.congratulations, reply_markup=await back_menu_kb())
    except Exception:
        await call.message.answer(text=all_text.gpt_error,
                                  reply_markup=await back_menu_kb())


def register_handler(dp: Dispatcher):
    dp.callback_query.register(go_photo, F.data == 'new_photo')
    dp.message.register(get_first_photo, FSMPhoto.go_photo, F.content_type == 'photo')
    dp.message.register(go_photo_from_answers, FSMAnswer.third_answer)
    dp.callback_query.register(new_photo, F.data == 'go')
