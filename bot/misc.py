from aiogram import Bot, Dispatcher
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from configs.bot import BotConfig


bot = Bot(token=BotConfig().api_token.get_secret_value())
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())
