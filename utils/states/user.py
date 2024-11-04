from aiogram.fsm.state import State, StatesGroup


class FSMPhone(StatesGroup):
    get_phone_number = State()


class FSMAnswer(StatesGroup):
    first_answer = State()
    second_answer = State()
    third_answer = State()

class FSMPhoto(StatesGroup):
    go_photo = State()

