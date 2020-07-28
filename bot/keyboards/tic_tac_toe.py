import json
from typing import Dict, Optional

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


async def create_filed(game_id: int, positions: Optional[Dict[int, str]] = None) -> InlineKeyboardMarkup:
    if not positions:
        positions = {}
    signs = {'cross': '❌', 'circle': '⭕️', 'empty': '⬜️'}
    buttons = (
        InlineKeyboardButton(
            signs[positions.get(position, 'empty')],
            callback_data=json.dumps({
                'name': 'xo_field',
                'game_id': game_id,
                'pos': position
            }).replace(' ', '')
        )
        for position in range(9)
    )

    return InlineKeyboardMarkup().add(*buttons)


async def create_sign_selection(
        game_starter_id: int,
        game_id: Optional[int] = None,
        selected_sign: Optional[str] = None
) -> InlineKeyboardMarkup:
    signs = {'cross': ('❌', 'x'), 'circle': ('⭕️', 'o')}
    signs.pop(selected_sign, None)
    buttons = (
        InlineKeyboardButton(
            sign,
            callback_data=json.dumps(
                {
                    'name': 'xo_sign',
                    'id': game_starter_id,
                    'sign': sign_name,
                    'game': game_id
                }
            ).replace(' ', '')
        )
        for sign, sign_name in signs.values()
    )

    return InlineKeyboardMarkup().add(*buttons)
