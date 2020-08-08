import json
from typing import Dict, Optional

from aiogram.types import CallbackQuery

from DAO import (
    UserDAO,
    TicTacToeGameDAO,
    TicTacToePlayerDAO,
    TicTacToeStepDAO
)
from constants import CACHE_TIME
from keyboards.tic_tac_toe import create_filed, create_sign_selection
from misc import dp
from models import (
    EnumSign,
    EnumStatus,
    TicTacToePlayer,
    TicTacToeStep,
    User
)


async def check_win(steps: Dict[int, str]) -> Optional[str]:
    base_field = [[None for _ in range(3)] for _ in range(3)]
    for position, sign in steps.items():
        base_field[position // 3][position % 3] = sign

    def check_row(row):
        sign = row[0]
        return sign if all(item == sign and item for item in row) else None

    for field in (base_field, zip(*base_field)):
        for row in field:
            if sign := check_row(row):
                return sign

    main_diagonal = [base_field[i][i] for i in range(3)]
    side_diagonal = [row[index] for row, index in zip(base_field, range(-1, -4, -1))]

    for diagonal in (main_diagonal, side_diagonal):
        if sign := check_row(diagonal):
            return sign

    return None


async def create_end_game_field(steps: Dict[int, str]) -> str:
    signs = {'cross': '❌', 'circle': '⭕️', None: '⬜️'}

    field = [[None for _ in range(3)] for _ in range(3)]
    for row_index, row in enumerate(field):
        for column_index, _ in enumerate(row):
            row[column_index] = signs[steps.get(row_index * 3 + column_index)]

    return '\n'.join([''.join(row) for row in field])


async def create_players_caption_template(cross: str = '❓', circle: str = '❓') -> str:
    return f'❌ {cross}\n⭕️ {circle}'


async def create_players_end_game_template(cross: str, circle: str, winner: Optional[str] = None) -> str:
    if not winner:
        cross_status = circle_status = '🤝'
    else:
        cross_status = '🎉' if winner == cross else '💩'
        circle_status = '🎉' if winner == circle else '💩'
    return f'❌ {cross}️ {cross_status}\n⭕{circle} {circle_status}'


def callback_filter_by_name(query: CallbackQuery, name: str) -> bool:
    query_data = json.loads(query.data)
    return query_data['name'] == name


@dp.callback_query_handler(lambda query: callback_filter_by_name(query, 'xo_sign'))
async def sign_creation(query: CallbackQuery):
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    button_data = json.loads(query.data)
    sign_value = 'cross' if button_data['sign'] == 'x' else 'circle'
    sign = EnumSign[sign_value]
    user = await UserDAO().get_or_create(name=user_name, tg_id=user_id)

    if button_data['id'] == user_id:
        if button_data['game']:
            await query.answer(
                text='Вы уже выбрали сторону. Ждите 🕘🕥',
                show_alert=True,
                cache_time=CACHE_TIME
            )
        else:
            game = await TicTacToeGameDAO().create(
                current_step_user_id=user['User_id'] if sign == EnumSign.cross else None
            )
            await TicTacToePlayerDAO().create(
                user_id=user['User_id'],
                game_id=game['TicTacToeGame_id'],
                sign=sign
            )
            await query.bot.edit_message_text(
                text=await create_players_caption_template(**{sign_value: user_name}),
                inline_message_id=query.inline_message_id,
                reply_markup=await create_sign_selection(
                    button_data['id'],
                    game['TicTacToeGame_id'],
                    selected_sign=sign_value
                )
            )
            await query.answer()
    else:
        if game_id := button_data['game']:
            game = await TicTacToeGameDAO().get(id=game_id)
            current_step_user_id = game['TicTacToeGame_current_step_user_id'] or user['User_id']
            await TicTacToePlayerDAO().create(
                user_id=user['User_id'],
                game_id=game['TicTacToeGame_id'],
                sign=sign
            )
            await TicTacToeGameDAO().update_by_id(
                game_id,
                current_step_user_id=current_step_user_id,
                status=EnumStatus.in_progress
            )
            players = await TicTacToePlayerDAO().get_many(
                joins=[(TicTacToePlayer, User, TicTacToePlayer.user_id == User.id)],
                game_id=game_id
            )
            player_signs = {player['TicTacToePlayer_sign']: player['User_name'] for player in players}
            await query.bot.edit_message_text(
                text=await create_players_caption_template(**player_signs),
                inline_message_id=query.inline_message_id,
                reply_markup=await create_filed(game['TicTacToeGame_id'])
            )
            await query.answer()
        else:
            await query.answer(
                text='Первым выбирает сторону создатель игры. Ждите 🕘🕥',
                show_alert=True,
                cache_time=CACHE_TIME
            )


@dp.callback_query_handler(lambda query: callback_filter_by_name(query, 'xo_field'))
async def game(query: CallbackQuery):
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    button_data = json.loads(query.data)
    game = await TicTacToeGameDAO().get(id=button_data['game_id'])
    user = await UserDAO().get_or_create(name=user_name, tg_id=user_id)
    players = await TicTacToePlayerDAO().get_many(
        joins=[(TicTacToePlayer, User, TicTacToePlayer.user_id == User.id)],
        game_id=button_data['game_id']
    )

    players_tg_ids = [player['User_tg_id'] for player in players]
    if user_id not in players_tg_ids:
        await query.answer(
            text='Вы не принимаете участия в этой игре',
            show_alert=True,
            cache_time=CACHE_TIME
        )

    if user['User_id'] == game['TicTacToeGame_current_step_user_id']:
        step = await TicTacToeStepDAO().get(
            joins=[(TicTacToeStep, TicTacToePlayer, TicTacToeStep.player_id == TicTacToePlayer.id)],
            game_id=(TicTacToePlayer, game['TicTacToeGame_id']),
            position=button_data['pos']
        )
        if step:
            await query.answer(
                text='Клетка занята. Выберите другую',
                show_alert=True,
                cache_time=CACHE_TIME
            )
        else:
            current_player = next(filter(lambda player: player['User_tg_id'] == user_id, players))
            next_player = next(filter(lambda player: player['User_tg_id'] != user_id, players))
            await TicTacToeStepDAO().create(
                position=button_data['pos'],
                player_id=current_player['TicTacToePlayer_id']
            )

            steps = await TicTacToeStepDAO().get_many(
                joins=[(TicTacToeStep, TicTacToePlayer, TicTacToeStep.player_id == TicTacToePlayer.id)],
                game_id=(TicTacToePlayer, game['TicTacToeGame_id'])
            )
            positions = {step['TicTacToeStep_position']: step['TicTacToePlayer_sign'] for step in steps}
            players_signs = {player['TicTacToePlayer_sign']: player['User_name'] for player in players}

            end_game_template = None
            if sign := await check_win(positions):
                if current_player['TicTacToePlayer_sign'] == sign:
                    winner, looser = current_player, next_player
                else:
                    winner, looser = next_player, current_player
                await TicTacToePlayerDAO().update_by_id(winner['TicTacToePlayer_id'], is_winner=True)
                await TicTacToePlayerDAO().update_by_id(looser['TicTacToePlayer_id'], is_winner=False)
                end_game_template = await create_players_end_game_template(**players_signs, winner=winner['User_name'])
            elif len(positions) == 9:
                await TicTacToePlayerDAO().update_by_id(current_player['TicTacToePlayer_id'], is_winner=False)
                await TicTacToePlayerDAO().update_by_id(next_player['TicTacToePlayer_id'], is_winner=False)
                end_game_template = await create_players_end_game_template(**players_signs)

            if end_game_template:
                await TicTacToeGameDAO().update_by_id(game['TicTacToeGame_id'], status=EnumStatus.finished)
                field = await create_end_game_field(positions)
                await query.bot.edit_message_text(
                    text=f'{end_game_template}\n\n{field}',
                    inline_message_id=query.inline_message_id,
                )
                await query.answer()
                return None

            await query.bot.edit_message_reply_markup(
                inline_message_id=query.inline_message_id,
                reply_markup=await create_filed(game['TicTacToeGame_id'], positions)
            )

            await TicTacToeGameDAO().update_by_id(
                game['TicTacToeGame_id'],
                current_step_user_id=next_player['User_id']
            )
            await query.answer()
    else:
        await query.answer(
            text='Сейчас не ваш ход. Ждите 🕘🕥',
            show_alert=True,
            cache_time=CACHE_TIME
        )
