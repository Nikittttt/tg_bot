import logging
import requests
import re
from asyncio import get_event_loop

from aiogram import executor
from aiogram.types import InlineQuery, Message, ContentTypes
from asyncpgsa import pg
from bs4 import BeautifulSoup

import games.tic_tac_toe
from DAO import UserDAO
from configs import DataBaseConfig
from constants import CACHE_TIME
from inline_arcticles.articles import create_tic_tac_toe_inline_article
from misc import dp


logging.basicConfig(level=logging.INFO)


@dp.inline_handler()
async def main_inline(query: InlineQuery):
    item = await create_tic_tac_toe_inline_article(game_starter_id=query.from_user.id)
    await query.answer(results=[item], cache_time=CACHE_TIME, is_personal=True)


@dp.message_handler(content_types=ContentTypes.NEW_CHAT_MEMBERS)
async def new_chat_member(message: Message):
    users = {}
    user_db = UserDAO()
    for new_member in message.new_chat_members:
        if new_member.is_bot:
            continue
        else:
            user = user_db.get(tg_id=new_member.id)
            if not user:
                user = user_db.create(tg_id=new_member.id, name=new_member.full_name)
            users[new_member.id] = new_member.get_mention(name=user.name)

    chat_name = message.chat.full_name

    if users:
        list_users = list(users.values())
        if len(users.values()) == 1:
            str_users = str(list_users[0])
        else:
            almost_all_lines = ", ".join(list_users[:len(users.values()) - 1])
            str_users = f"{almost_all_lines} и {list_users[-1]}"
        await message.reply(f"Давайте все вместе поприветствуем {str_users} "
                            f"в нашем уютном чате <{chat_name}>")


@dp.message_handler(content_types=types.ContentTypes.LEFT_CHAT_MEMBER)
async def left_chat_member(message: types.Message):
    bot_me = await message.bot.get_me()

    if message.from_user.id == bot_me.id or message.left_chat_member.is_bot:
        return None

    left_user = message.left_chat_member

    user_db = UserDAO()
    user = user_db.get(tg_id=left_user.id)
    if not user:
        user = user_db.create(tg_id=left_user.id, name=left_user.full_name)

    user_link = left_user.get_mention(name=user.name)
    if message.left_chat_member.id == message.from_user.id:
        await message.answer(f"Press F to pay respect {user_link}")
    else:
        await message.answer(f"Видимо {user_link} это заслужил...")


@dp.message_handler(lambda message: message.get_args(), commands=['change_name'], content_types=types.ContentTypes.TEXT)
async def change_name(message: types.Message):
    from_user = message.from_user
    text = message.get_args()

    user_db = UserDAO()
    old_username = user_db.get(tg_id=from_user.id)
    if not old_username:
        old_username = user_db.create(tg_id=from_user.id, name=from_user.full_name)

    new_username = user_db.update_by_tg_id(tg_id=from_user.id, name=text)
    old_user_link = from_user.get_mention(name=old_username.name)
    new_user_link = from_user.get_mention(name=new_username.name)
    await message.answer(f"Теперь ты не {old_user_link}, а {new_user_link}")


@dp.message_handler(lambda message: message.get_args(), commands=['google'], content_types=types.ContentTypes.TEXT)
async def googling(message: types.Message):
    from_user = message.from_user
    text = message.get_args()

    user_db = UserDAO()
    username = user_db.get(tg_id=from_user.id)
    if not username:
        username = user_db.create(tg_id=from_user.id, name=from_user.full_name)

    url = f'https://www.google.com/search?lang=ru&q={text}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    tables = soup.find_all("a", href=re.compile('url\?q='))

    count_website = 0
    list_googling = []
    for website in tables:
        try:
            text_website = website.h3.div.get_text()
            link_website = website['href'][0:website['href'].rfind('&sa')].replace("/url?q=", "", 1)
            list_googling.append(f'{text_website} - {link_website}')
            count_website += 1
            if count_website == 5:
                break
        except AttributeError:
            continue
    if count_website == 0:
        text_googling = 'Мне не удалось найти ничего'
    else:
        str_from_list_googling = "\n".join(list_googling)
        text_googling = f'Мне удалось найти следующее:\n{str_from_list_googling}'

    user_link = from_user.get_mention(name=username.name)
    await message.answer(f"Уважаемый {user_link}, по вашему запросу <{text}>\n{text_googling}")


async def init_connection():
    db_config = DataBaseConfig()
    await pg.init(
        host=db_config.host,
        port=db_config.port,
        database=db_config.name,
        user=db_config.user,
        password=db_config.password.get_secret_value(),
        min_size=5,
        max_size=10
    )


if __name__ == '__main__':
    event_loop = get_event_loop()
    event_loop.run_until_complete(init_connection())
    executor.start_polling(dp, loop=event_loop, skip_updates=True)
