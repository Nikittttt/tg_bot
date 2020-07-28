from typing import List

from asyncpg import Record
from asyncpgsa import pg
from sqlalchemy import sql

from models import (
    User,
    TicTacToeGame,
    TicTacToePlayer,
    EnumSign,
    TicTacToeStep
)


class BaseDAO:
    async def _generate_select(self, model, **fields) -> sql.Select:
        """
        :param model: SqlAlchemy model
        :param fields: fields to filter

        :return: SqlAlchemy Select object
        """
        fields_to_filter = []
        for field_name, field_value in fields.items():
            fields_to_filter.append(getattr(model, field_name) == field_value)
        return sql.select([model]).where(sql.and_(*fields_to_filter))


class UserDAO(BaseDAO):
    async def create(self, tg_id: int, name: str) -> Record:
        """
        :param tg_id: Telegram ID of the user
        :param name: Telegram Name of the user

        :return User record
        """
        query = sql.insert(User).values(tg_id=tg_id, name=name)
        return await pg.fetchrow(query)

    async def get_many(self, **fields) -> List[Record]:
        """
        :param fields: fields to filter

        :return List of User records
        """
        query = await self._generate_select(User, **fields)
        return await pg.fetch(query)

    async def get(self, **fields) -> Record:
        """
        :param fields: fields to filter

        :return User record
        """
        query = await self._generate_select(User, **fields)
        return await pg.fetchrow(query)

    async def update_by_tg_id(self, tg_id: int, **fields) -> Record:
        """
        :param tg_id: Telegram ID of the user
        :param fields: Fields to update

        :return User record
        """
        query = sql.update(User).returning(User.id).where(User.tg_id == tg_id).values(fields)
        return await pg.fetchrow(query)

    async def delete(self, tg_id: int) -> None:
        """
        :param tg_id: Telegram ID of the user
        """
        query = sql.delete(User).where(User.tg_id == tg_id)
        return await pg.fetchrow(query)


class TicTacToeGameDAO(BaseDAO):
    async def create(self, user_id: int) -> Record:
        """
        :param user_id: ID of the user

        :return TicTacToe Game record
        """
        query = sql.insert(TicTacToeGame).values(current_step_user_id=user_id)
        return await pg.fetchrow(query)

    async def get_many(self, **fields) -> List[Record]:
        """
        :param fields: fields to filter

        :return List of TicTacToe Game records
        """
        query = await self._generate_select(TicTacToeGame, **fields)
        return await pg.fetch(query)

    async def get(self, **fields) -> Record:
        """
        :param fields: fields to filter

        :return TicTacToe Game record
        """
        query = await self._generate_select(TicTacToeGame, **fields)
        return await pg.fetchrow(query)

    async def update_by_id(self, game_id: int, **fields) -> Record:
        """
        :param game_id: ID of the TicTacToe Game
        :param fields: Fields to update

        :return TicTacToe Game record
        """
        query = sql.update(TicTacToeGame).returning(TicTacToeGame.id).where(
            TicTacToeGame.id == game_id
        ).values(fields)
        return await pg.fetchrow(query)

    async def delete(self, game_id: int) -> None:
        """
        :param game_id: ID of the TicTacToe Game
        """
        game = sql.delete(TicTacToeGame).where(TicTacToeGame.id == game_id)
        return await pg.fetchrow(game)


class TicTacToePlayerDAO(BaseDAO):
    async def create(self, user_id: int, game_id: int, sign: EnumSign) -> Record:
        """
        :param user_id: ID of the user
        :param game_id: ID of the TicTacToe Game
        :param sign: cross or circle

        :return TicTacToe Player record
        """
        query = sql.insert(TicTacToePlayer).values(user_id=user_id, game_id=game_id, sign=sign)
        return await pg.fetchrow(query)

    async def get_many(self, **fields) -> List[Record]:
        """
        :param fields: fields to filter

        :return List of the TicTacToe Player records
        """
        query = await self._generate_select(TicTacToePlayer, **fields)
        return await pg.fetch(query)

    async def get(self, **fields) -> Record:
        """
        :param fields: fields to filter

        :return List of the TicTacToe Player records
        """
        query = await self._generate_select(TicTacToePlayer, **fields)
        return await pg.fetchrow(query)

    async def update(self, player_id: int, **fields) -> Record:
        """
        :param player_id: ID of the TicTacToe Player
        :param fields: fields to update

        :return TicTacToe Player record
        """
        query = sql.update(TicTacToePlayer).returning(TicTacToePlayer.id).where(
            TicTacToePlayer.id == player_id
        ).values(fields)
        return await pg.fetchrow(query)

    async def delete(self, player_id: int) -> None:
        """
        :param player_id: ID of the TicTacToe Player
        """
        query = sql.delete(TicTacToePlayer).where(TicTacToePlayer.id == player_id)
        return await pg.fetchrow(query)


class TicTacToeStepDAO(BaseDAO):
    async def create(self, player_id: int, position: int) -> Record:
        """
        :param player_id: ID of the TicTacToe player
        :param position: cell position

        :return TicTacToe Step record
        """
        query = sql.insert(TicTacToeStep).values(player_id=player_id, position=position)
        return await pg.fetchrow(query)

    async def get_many(self, **fields) -> List[Record]:
        """
        :param fields: fields to filter

        :return List of Step records
        """
        query = await self._generate_select(TicTacToeStep, **fields)
        return await pg.fetch(query)

    async def get(self, **fields) -> Record:
        """
        :param fields: fields to filter

        :return List of TicTacToe Step records
        """
        query = await self._generate_select(TicTacToeStep, **fields)
        return await pg.fetchrow(query)

    async def delete(self, step_id: int) -> None:
        """
        :param step_id: ID of TicTacToe Step
        """
        query = sql.delete(TicTacToeStep).where(TicTacToeStep.id == step_id)
        return await pg.fetchrow(query)
