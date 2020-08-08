import logging
from asyncio import get_event_loop

from aiogram import executor
from aiogram.types import InlineQuery
from asyncpgsa import pg

import games.tic_tac_toe
from configs import DataBaseConfig
from constants import CACHE_TIME
from inline_arcticles.articles import create_tic_tac_toe_inline_article
from misc import dp


logging.basicConfig(level=logging.INFO)


@dp.inline_handler()
async def main_inline(query: InlineQuery):
    item = await create_tic_tac_toe_inline_article(game_starter_id=query.from_user.id)
    await query.answer(results=[item], cache_time=CACHE_TIME, is_personal=True)


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
