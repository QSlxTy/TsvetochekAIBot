import json
import uuid

import yadisk
from openai import OpenAI

from bot_start import logger
from src.config import Configuration
from utils.RGB import rgb_result

GPT_PROMPT_ENG = f"""

Your task is to determine the parameters from a photograph of a face.

Gender: Female, Male
Age group: 14-20, 21-35, 36-45, 46-60, 60+
Eye color:
     "blue":
       "bright": "161, 202, 241",
       "muted": "82, 140, 158",
       "light": "184, 216, 225",
       "dark": "27, 86, 117",
       "soft": "53, 115, 136",
       "clear": "13, 152, 186"
     ,
     "gray":
       "bright": "222,222,222",
       "muted": "219,209,209",
       "light": "233,233,233",
       "dark": "128,128,128",
       "soft": "216,212,212",
       "clear": "208,208,208"
     ,
     "green":
       "bright": "25,163,55",
       "muted": "75,114,72",
       "light": "141,184,137",
       "dark": "69,79,7",
       "soft": "51,122,44",
       "clear": "181,210,158"
     ,
     "brown-yellow-green":
       "bright": "147,170,0",
       "muted": "133,151,75",
       "light": "184,163,0",
       "dark": "85,104,50",
       "soft": "160,154,12",
       "clear": "123,160,91"
     ,
     "light brown":
       "bright": "121,106,63",
       "muted": "113,99,68",
       "light": "137,123,76",
       "dark": "99,90,71",
       "soft": "94,88,64",
       "clear": "192,149,105"
     ,
     "brown":
       "bright": "96,49,1",
       "muted": "94,72,30",
       "light": "99,57,15",
       "dark": "69,24,0",
       "soft": "99,78,52",
       "clear": "84,42,14"
     ,
     "dark brown":
       "bright": "71,40,18",
       "muted": "60,34,16",
       "light": "84,48,22",
       "dark": "33,33,33",
       "soft": "91,58,41",
       "clear": "53,23,12"
     ,
     "blue-green":
       "bright": "62,180,137",
       "muted": "60,165,157",
       "light": "102,178,178",
       "dark": "49,102,80",
       "soft": "0,128,128",
       "clear": "0,155,119"

Presence of a ring around the iris: true, false
Eye white color:
     "Pure white": "255,255,255",
     "Snow White": "255,250,250",
     "Smoky White": "245,245,245",
     "Cream": "253,244,227",
     "Mint-cream": "245,255,250",
     "Ghost White": "248,248,255",
     "Ivory": "255,255,240",
     "Old Lace": "253,245,230",
     "Floral White": "255,250,240",
     "Sea Shell Color (Sea Foam)": "255,245,238",
     "Champagne color (Champagne)": "252,252,238",
     "Color of the silky thread-like pistils of the cobs of unripe corn": "255,248,220"


Hair color: brunette, red, blond, chestnut, light brown, gray, color dyeing



Answer in json format, replace "value" with the answer for each parameter:


   "Params":
     "Gender": Value
     "Age Group": Value
     "Eye color": [Value, Value, RGB]
     "Presence of a ring around the iris": Value
     "Eye white color": [Value, RGB]
     "Hair color": Value

    """

GPT_PROMPT_RU = f"""

Твоя задача, определить параметры по фотографии лица. 

пол: Женский, Мужской
Возрастная группа: 14-20, 21-35, 36-45, 46-60, 60 
Цвет глаз: 
    "голубые": 
      "яркий": "161, 202, 241",
      "приглушенный": "82, 140, 158",
      "светлый": "184, 216, 225",
      "темный": "27, 86, 117",
      "мягкий": "53, 115, 136",
      "ясный": "13, 152, 186"
    ,
    "серые": 
      "яркий": "222,222,222",
      "приглушенный": "219,209,209",
      "светлый": "233,233,233",
      "темный": "128,128,128",
      "мягкий": "216,212,212",
      "ясный": "208,208,208"
    ,
    "зеленые": 
      "яркий": "25,163,55",
      "приглушенный": "75,114,72",
      "светлый": "141,184,137",
      "темный": "69,79,7",
      "мягкий": "51,122,44",
      "ясный": "181,210,158"
    ,
    "буро-желто-зеленые": 
      "яркий": "147,170,0",
      "приглушенный": "133,151,75",
      "светлый": "184,163,0",
      "темный": "85,104,50",
      "мягкий": "160,154,12",
      "ясный": "123,160,91"
    ,
    "светло-карие": 
      "яркий": "121,106,63",
      "приглушенный": "113,99,68",
      "светлый": "137,123,76",
      "темный": "99,90,71",
      "мягкий": "94,88,64",
      "ясный": "192,149,105"
    ,
    "карие": 
      "яркий": "96,49,1",
      "приглушенный": "94,72,30",
      "светлый": "99,57,15",
      "темный": "69,24,0",
      "мягкий": "99,78,52",
      "ясный": "84,42,14"
    ,
    "темно-карие": 
      "яркий": "71,40,18",
      "приглушенный": "60,34,16",
      "светлый": "84,48,22",
      "темный": "33,33,33",
      "мягкий": "91,58,41",
      "ясный": "53,23,12"
    ,
    "сине-зеленые": 
      "яркий": "62,180,137",
      "приглушенный": "60,165,157",
      "светлый": "102,178,178",
      "темный": "49,102,80",
      "мягкий": "0,128,128",
      "ясный": "0,155,119"

Наличие кольца вокруг радужки: да, нет  
Цвет белка глаза: 
    "Чисто-белый": "255,255,255",
    "Белоснежный": "255,250,250",
    "Дымчато-белый": "245,245,245",
    "Кремовый": "253,244,227",
    "Мятно-кремовый": "245,255,250",
    "Призрачно-белый": "248,248,255",
    "Слоновая кость": "255,255,240",
    "Старое кружево": "253,245,230",
    "Цветочный белый": "255,250,240",
    "Цвет Морской раковины (Морская пена)": "255,245,238",
    "Цвет Шампанского (Шампань)": "252,252,238",
    "Цвет Шелковистых нитевидных пестиков початков неспелой кукурузы": "255,248,220"


Цвет волос: брюнет, рыжий, блондин, каштановый, русый, седой, цветное окрашивание  



Отвечай в формате json, замени "value" ответом на каждый параметр :
Заполняй строго по шаблону и не отклоняйся

  "Params": 
    "Пол": Value
    "Возрастная группа": Value
    "Цвет глаз": [Value, [R,G,B]]
    "Наличие кольца вокруг радужки": Value
    "Цвет белка глаза": [Value, RGB]
    "Цвет волос": Value


   """

RECOMMENDATION_PROMPT = ("Дай рекомендации для {GPT_vision} - тут то, что приходит от модели вижен. Учитывай в своем"
                         " ответе триаду цветов {triada}, но не говори об этом. Учитывай текущее время года:"
                         " {month, year}.  Начни свой ответ так: Привет, Цветочек! На основе твоих данных я составил"
                         " цветовые рекомендации для тебя! ")
SYSTEM_PROMPT = ("Действуй в роли стилиста-имиджмейкера. Используй свои знания в области колористики, уникальное "
                 "чувство стиля и познания о моде для создания ярких и привлекательных образов, помощи в подборе "
                 "сочетания цветов или создании собственного образа. Я опишу тебе свои параметры и триаду моих "
                 "цветов на основании цвета глаз, а ты опишешь всё детально, предложишь различные варианты сочетания "
                 "одежды, аксессуаров, макияжа, маникюра и причёски в зависимости от ситуации. Структурируй свой"
                 " ответ в формате: Цветовая гамма одежды, Макияж, Прическа и цвет волос, Аксессуары, Особенности стиля."
                 " Не превышай длину ответа в 4000 символов ")
GPT_API_KEY = Configuration.gpt_api_key
client = OpenAI(
    api_key=GPT_API_KEY)


async def GPT_vision(image):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": GPT_PROMPT_RU},
                    {
                        "type": "image_url",
                        "image_url": {"url": image}
                    },
                ],
            }
        ],
        max_tokens=300,
    )
    return response


async def recom_gpt(user_prompt, system_prompt, image):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": image}}

                ],
            },
            {"role": "system",
             "content": system_prompt}
        ],
        max_tokens=3000,
        stream=False,
        temperature=0.5,

    )
    return response


async def json_load(image, user_id):
    print(image)
    response = await GPT_vision(image)
    res = response.json()
    content = json.loads(res)
    if content.get('choices'):
        first_choice = content['choices'][0]
        if first_choice.get('message'):
            content = first_choice['message']['content']
            # Удаление технических символов, таких как обратные косые черты и символы новой строки
            readable_content = content.replace("\\n", "\n").replace("\\", "").replace('```', '').replace('json',
                                                                                                         '').replace(
                '\n', '').replace('  ', '').replace('    ', '')

            data = json.loads(readable_content)
            # Получение РГБ глаз
            rgb = data["Params"]["Цвет глаз"][1]
            # ЗАкидывание РГБ глаза в обработку и составление триады
            answer = await rgb_result(rgb, user_id)
            if 'error' in answer:
                return 'error', 'error', 'error'
            else:
                unique_id = str(uuid.uuid4())
                url_color, path = await upload_image_telegraph(f"files/photos/{user_id}/triad.png", unique_id)
                rec_content = str(f'{readable_content}' + f'{RECOMMENDATION_PROMPT}')
                # Получение цветовой рекоммендации
                rec_content = await recom_gpt(rec_content, SYSTEM_PROMPT, url_color)
                await delete_file(path)
                rec_content = rec_content.choices[0].message.content
                rec_content = rec_content.replace('#', '').replace('*', '')
                return rec_content, url_color, readable_content


yandex = yadisk.YaDisk(token=Configuration.yadisk_token)


async def upload_file(file_path, yandex_path):
    logger.info(f"Start upload file to drop box")
    with open(file_path, 'rb'):
        yandex.upload(file_path, yandex_path)
    logger.info(f"File {file_path} uploaded to {yandex_path}")


async def create_shared_link(yandex_path):
    url = yandex.get_download_link(yandex_path)
    logger.info(f'link created {url}')

    return url


async def delete_file(yandex_path):
    try:
        yandex.remove(yandex_path)
        logger.info(f"File --> {yandex_path} deleted")
    except Exception as _ex:
        logger.error(f"Error delete file --> {_ex}")


async def upload_image_telegraph(local_file_path, yadisk_name):
    await upload_file(local_file_path, f'/{yadisk_name}')
    link = await create_shared_link(f'/{yadisk_name}')
    return link, f'/{yadisk_name}'
