from asyncio import get_event_loop

from aiogram import Bot, Dispatcher, executor, types
from asyncpgsa import pg

from configs.bot import BotConfig
from configs.database import DataBaseConfig

bot = Bot(token=BotConfig().api_token.get_secret_value())
dp = Dispatcher(bot)


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


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
