from aiogram.types import (
    InlineQueryResultArticle,
    InputTextMessageContent
)

from games.tic_tac_toe import create_players_caption_template
from keyboards.tic_tac_toe import create_sign_selection


async def create_tic_tac_toe_inline_article(game_starter_id: int):
    article = InlineQueryResultArticle(
        id='1',
        title='Tic Tac Toe',
        description='Tic Tac Toe Game',
        input_message_content=InputTextMessageContent(await create_players_caption_template()),
        reply_markup=await create_sign_selection(game_starter_id)
    )
    return article
