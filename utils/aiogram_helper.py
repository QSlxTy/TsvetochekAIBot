from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import List, Optional, Union, Literal

    from aiogram.types import InlineQuery, User, MessageEntity
    from aiogram.fsm.context import FSMContext
    from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
    from aiogram.exceptions import TelegramRetryAfter
    from aiogram.utils.keyboard import InlineKeyboardMarkup

from aiogram import Bot
from aiogram.types.base import UNSET_DISABLE_WEB_PAGE_PREVIEW, UNSET_PROTECT_CONTENT, UNSET_PARSE_MODE
from aiogram.types import InputMediaPhoto, InputMediaDocument, InputMediaAnimation, InputMediaVideo
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.utils.markdown import hlink
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
import asyncio

from bot_start import dp, bot


def generate_user_hlink(update: Union[Message, CallbackQuery] = None,
                        user_id: int = None,
                        user_name: str = None,
                        text_link: str = None) -> Optional[str]:
    if update:
        text_link = update.from_user.full_name
        url_link = f'tg://user?id={update.from_user.id}'
        user_name = update.from_user.username
    else:
        if not user_id or not text_link:
            raise AttributeError('User id and text link is not None')
        url_link = f'tg://user?id={user_id}'
    more_info = f'(@{user_name})' if user_name else ''
    url_user = hlink(text_link, url_link)
    hlink_user = f'{url_user} {more_info}'
    return hlink_user


def generate_hlink(text_link: str, url_link: str) -> hlink:
    link = hlink(text_link, url_link)
    return link


def repack_keyboard(buttons: list):
    repack_buttons = []
    for button in buttons:
        if button[1] == 'call':
            repack_buttons.append([InlineKeyboardButton(text=button[0], callback_data=button[2])])
        elif button[1] == 'url':
            repack_buttons.append([InlineKeyboardButton(text=button[0], url=button[2])])
        elif button[1] == 'inline':
            repack_buttons.append([InlineKeyboardButton(text=button[0], switch_inline_query_current_chat=button[2])])
    return repack_buttons


def create_inline(buttons: list, adjust: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardBuilder(markup=repack_keyboard(buttons))
    return markup.adjust(adjust).as_markup(resize_keyboard=True)


def generate_rows_markup(buttons: list, rows: list) -> List[List[InlineKeyboardButton]] | str:
    markup = []
    counter_button = 0
    for i in range(0, len(rows)):
        buttons_row = []
        for i2 in range(rows[i]):
            try:
                buttons_row.append(buttons[counter_button][0])
                counter_button += 1
            except IndexError:
                raise AttributeError('ERROR: Wrong rows specified')
        markup.append(buttons_row)
    return markup


def create_inline_rows(buttons: list, rows: list) -> str | InlineKeyboardMarkup:
    markup = generate_rows_markup(repack_keyboard(buttons), rows)
    markup = InlineKeyboardBuilder(markup=markup)
    return markup.as_markup(resize_keyboard=True)


async def generate_url_buttons(buttons_info: List[List[str]]) -> InlineKeyboardMarkup:
    buttons = []
    for button in buttons_info:
        buttons.append([InlineKeyboardButton(text=button[0], url=button[1])])
    markup = await create_inline(buttons, 1)
    return markup


async def get_bot_data(bot_object: Bot) -> User:
    return await bot_object.me()


async def delete_message(event: Union[CallbackQuery, Message] = False,
                         user_id: Optional[int] = 0,
                         message_id: Optional[int] = 0,
                         try_redact: bool = True):
    if event:
        user_id = event.from_user.id
        if isinstance(event, CallbackQuery):
            message_id = event.message.message_id
        else:
            message_id = event.message_id
    else:
        if not message_id:
            raise AttributeError('Message ID is None!')
    try:
        await bot.delete_message(user_id, message_id)
        return True
    except TelegramAPIError:
        if try_redact:
            try:
                await bot.edit_message_text('🗑', user_id, message_id)
                return True
            except TelegramAPIError:
                return False
        else:
            return False


async def inline_helper(query: InlineQuery, results: list[list[str, str, Optional[str], str]], no_result: int = 0):
    """
    :param no_result: minimum number of results
    :param query: event InlineQuery
    :param results: list[title, description, url, message_text]
    :return:
    """
    offset = int(query.offset) if query.offset else 0
    offset_results = results[offset:offset+50]
    articles = []
    article_index = 0
    for result in offset_results:
        if article_index == 50:
            break
        articles.append(InlineQueryResultArticle(
            id=str(article_index),
            title=result[0],
            description=result[1],
            thumb_url=result[2],
            input_message_content=InputTextMessageContent(message_text=result[3])
        ))
        article_index += 1
    if len(results) > offset + 50:
        await query.answer(articles, cache_time=1, is_personal=True, next_offset=str(offset + 50))
    else:
        if len(results) == no_result:
            articles.append(InlineQueryResultArticle(
                id=str(no_result), title='🎉Нет', description='Список пуст',
                thumb_url='https://cdn-icons-png.flaticon.com/512/7214/7214241.png',
                input_message_content=InputTextMessageContent(message_text='/start')))
        await query.answer(articles, cache_time=1, is_personal=True)


async def edit_text(
        message: Message,
        text: str,
        inline_message_id: Optional[str] = None,
        parse_mode: Optional[str] = UNSET_PARSE_MODE,
        entities: Optional[List[MessageEntity]] = None,
        disable_web_page_preview: Optional[bool] = UNSET_DISABLE_WEB_PAGE_PREVIEW,
        reply_markup: Optional[InlineKeyboardMarkup] = None):
    try:
        msg = await message.edit_text(
            text=text, inline_message_id=inline_message_id, parse_mode=parse_mode, entities=entities,
            disable_web_page_preview=disable_web_page_preview, reply_markup=reply_markup)
        return msg
    except TelegramAPIError as _ex:
        return False


async def send_message(
        chat_id: Union[int, str],
        text: str,
        message_thread_id: Optional[int] = None,
        parse_mode: Optional[str] = UNSET_PARSE_MODE,
        entities: Optional[List[MessageEntity]] = None,
        disable_web_page_preview: Optional[bool] = UNSET_DISABLE_WEB_PAGE_PREVIEW,
        disable_notification: Optional[bool] = None,
        protect_content: Optional[bool] = UNSET_PROTECT_CONTENT,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: Optional[bool] = None,
        reply_markup: Optional[
            Union[InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply]
        ] = None,
        request_timeout: Optional[int] = None) -> TelegramAPIError | Message:
    try:
        message = await bot.send_message(
            chat_id=chat_id, text=text, message_thread_id=message_thread_id, parse_mode=parse_mode, entities=entities,
            disable_web_page_preview=disable_web_page_preview, disable_notification=disable_notification,
            protect_content=protect_content, reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=allow_sending_without_reply, reply_markup=reply_markup,
            request_timeout=request_timeout)
        return message
    except TelegramAPIError as err:
        return err


def input_media(media_type: str, media: str, caption: str):
    match media_type:
        case 'photo':
            return InputMediaPhoto(media=media, caption=caption)
        case 'document':
            return InputMediaDocument(media=media, caption=caption)
        case 'animation':
            return InputMediaAnimation(media=media, caption=caption)
        case 'video':
            return InputMediaVideo(media=media, caption=caption)


async def message_constructor(chat_id: int, data: dict):
    text, files, buttons = data['text'], data['files'], data['buttons']
    buttons = create_inline(buttons, 1)
    try:
        if len(files) > 1:
            media_group = []
            for i in range(len(files)):
                file_type, file_id = files[i][0], files[i][1]
                caption = text if (i == 0 and text) else None
                media_group.append(input_media(media_type=file_type, media=file_id, caption=caption))
            messages: list[Message] = await bot.send_media_group(chat_id=chat_id, media=media_group)
            return messages
        else:
            if len(files) == 0:
                message = await bot.send_message(chat_id=chat_id, text=text, reply_markup=buttons)
            else:
                match files[0][0]:
                    case 'photo':
                        message = await bot.send_photo(chat_id=chat_id, photo=files[0][1],
                                                       caption=text, reply_markup=buttons)
                    case 'video':
                        message = await bot.send_video(chat_id=chat_id, video=files[0][1],
                                                       caption=text, reply_markup=buttons)
                    case 'document':
                        message = await bot.send_document(chat_id=chat_id, document=files[0][1],
                                                          caption=text, reply_markup=buttons)
                    case _:
                        message = await bot.send_animation(chat_id=chat_id, animation=files[0][1],
                                                           caption=text, reply_markup=buttons)
            return [message]
    except TelegramRetryAfter as body:
        await asyncio.sleep(body.retry_after)
        return await message_constructor(chat_id, data)
    except TelegramAPIError:
        return False


async def get_state(chat_id: int, user_id: int) -> FSMContext:
    return dp.fsm.resolve_context(bot, chat_id=chat_id, user_id=user_id)


def unpack_media_group(messages: List[Message], special_format: Literal['no_caption', 'input_media'] = False):
    media_files = []
    for message in messages:
        if message.document:
            media_files.append(['document', message.document.file_id, message.html_text])
        elif message.photo:
            media_files.append(['photo', message.photo[-1].file_id, message.html_text])
        elif message.audio:
            media_files.append(['audio', message.audio.file_id, message.html_text])
        elif message.animation:
            media_files.append(['animation', message.animation.file_id, message.html_text])
        elif message.video:
            media_files.append(['video', message.video.file_id, message.html_text])
    if special_format:
        if special_format == 'no_caption':
            media_files = [[message[0], message[1]] for message in media_files]
        elif special_format == 'input_media':
            media_files = [input_media(media[0], media[1], media[2]) for media in media_files]
    return media_files


kb_delete_message = create_inline([['✅Прочитано', 'call', 'client_delete_message']], 1)
