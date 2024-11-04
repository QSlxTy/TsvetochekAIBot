from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


async def back_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    return builder.as_markup()

async def back_support_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='🔙 Назад', callback_data='support')
    return builder.as_markup()


async def get_phone_kb():
    builder = ReplyKeyboardBuilder()
    builder.button(text='Поделиться контактом', request_contact=True)
    return builder.as_markup(resize_keyboard=True)


async def menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📷 Загрузить новую фотографию", callback_data="new_photo")
    builder.button(text="🌸 Мои цвета ", callback_data="my_colors")
    builder.button(text="📋 Тарифы", callback_data="tariffs")
    builder.button(text="❓ Поддержка", callback_data="support")
    builder.adjust(1)
    return builder.as_markup()


async def support_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Как это работает?", callback_data="how_work")
    builder.button(text="📞 Обратная связь", callback_data="feedback")
    builder.button(text='🔙 Назад', callback_data='main_menu')
    builder.adjust(1)
    return builder.as_markup()


async def get_poll_answers_kb(poll_answers):
    builder = ReplyKeyboardBuilder()
    for poll_answer in poll_answers:
        builder.button(text=poll_answer, callback_data='second')
    builder.adjust(1)
    return builder.as_markup()


async def after_generation_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="📷 Попробовоть другое фото", callback_data="new_photo")
    builder.button(text='🔙 В главное меню', callback_data='main_menu')
    builder.adjust(1)
    return builder.as_markup()


async def go_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text='👍 Давай', callback_data='go')
    return builder.as_markup()

async def switch_photo_kb(count: int, len_data):
    builder = InlineKeyboardBuilder()
    if count == 0:
        builder.button(text='Вперёд', callback_data='my_colors:next')
        builder.button(text='В меню', callback_data='main_menu')
        builder.adjust(1)
    elif count == len_data:
        builder.button(text='Назад', callback_data='my_colors:back')
        builder.button(text='В меню', callback_data='main_menu')
        builder.adjust(1)
    else:
        builder.button(text='Назад', callback_data='my_colors:back')
        builder.button(text='Вперёд', callback_data='my_colors:next')
        builder.button(text='В меню', callback_data='main_menu')
        builder.adjust(1)
