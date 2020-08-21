import logging
from asyncio import get_event_loop

from aiogram import executor
from aiogram.types import InlineQuery, Message, ContentTypes
from asyncpgsa import pg

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

    if len(users.values()) > 0:
        if len(users.values()) == 1:
            str_users = str(list(users.values())[0])
        else:
            str_users = ", ".join(users.values()[:len(users.values()) - 1]) + " и " + list(users.values())[-1]
        await message.reply(("Давайте все вместе поприветствуем {users} "
                             "в нашем уютном чате <{chat_name}>").format(users=str_users, chat=chat_name))


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

    if message.left_chat_member.id == message.from_user.id:
        await message.answer("Press F to pay respect {user}".format(user=left_user.get_mention(name=user.name)))
    else:
        await message.answer("Видимо {user} это заслужил...".format(user=left_user.get_mention(name=user.name)))


@dp.message_handler(lambda message: message.get_args(), commands=['change_name'], content_types=types.ContentTypes.TEXT)
async def change_name(message: types.Message):
    from_user = message.from_user
    text = message.get_args()

    user_db = UserDAO()
    old_username = user_db.get(tg_id=from_user.id)
    if not old_username:
        old_username = user_db.create(tg_id=from_user.id, name=from_user.full_name)

    new_username = user_db.update_by_tg_id(tg_id=from_user.id, name=text)
    await message.answer("Теперь ты не {old_username}, а {new_username}".format(
        old_username=from_user.get_mention(name=old_username.name),
        new_username=from_user.get_mention(name=new_username.name)
    ))


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
