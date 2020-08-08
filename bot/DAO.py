from itertools import chain
from typing import List, Optional, Tuple

from asyncpg import Record
from asyncpgsa import pg
from sqlalchemy import sql

from models import (
    User,
    TicTacToeGame,
    TicTacToePlayer,
    TicTacToeStep
)


class BaseDAO:
    async def _generate_select(self, joins: Optional[List[Tuple]] = (), **filters) -> sql.Select:
        """
        :param filters: fields to filter

        :return: SqlAlchemy Select object
        """
        to_select_models = {self.model, *chain(*[join[:-1] for join in joins])}
        to_select = []
        for model in to_select_models:
            to_select.extend(
                [
                    field.label('_'.join((model.__tablename__, field.description)))
                    for field in list(model.__table__.columns)
                ]
            )

        fields_to_filter = []
        for field_name, field_value in filters.items():
            if isinstance(field_value, tuple):
                model, value = field_value
                fields_to_filter.append(getattr(model, field_name) == value)
            else:
                fields_to_filter.append(getattr(self.model, field_name) == field_value)
        query = sql.select(to_select)
        for join_args in joins:
            join = sql.join(*join_args)
            query = query.select_from(join)

        return query.where(sql.and_(*fields_to_filter))

    async def create(self, **fields) -> Record:
        query = sql.insert(self.model).returning(
            *[
                column.label('_'.join((self.model.__tablename__, column.description)))
                for column in self.model.__table__.columns
            ]
        ).values(**fields)
        return await pg.fetchrow(query)

    async def get_or_create(self, joins: Optional[List[Tuple]] = (), **fields) -> Record:
        record = await self.get(joins, **fields)
        if not record:
            record = await self.create(**fields)

        return record

    async def get(self, joins: Optional[List] = (), **fields) -> Record:
        """
        :param joins: list of joins
        :param fields: fields to filter

        :return: Record object
        """
        query = await self._generate_select(joins=joins, **fields)
        return await pg.fetchrow(query)

    async def get_many(self, joins: Optional[List] = (), **fields) -> List[Record]:
        """
        :param joins: list of joins
        :param fields: fields to filter

        :return List of Record objects
        """
        query = await self._generate_select(joins=joins, **fields)
        return await pg.fetch(query)

    async def update_by_id(self, record_id, **fields) -> Record:
        """
        :param record_id: database record ID
        :param fields: Fields to update

        :return SqlAlchemy model record
        """

        query = sql.update(self.model).returning(self.model.id).where(self.model.id == record_id).values(fields)
        return await pg.fetchrow(query)

    async def delete_by_id(self, record_id: int) -> None:
        """
        :param record_id: database record ID
        """
        query = sql.delete(User).where(self.model.id == record_id)
        return await pg.fetchrow(query)


class UserDAO(BaseDAO):
    def __init__(self):
        self.model = User

    async def update_by_tg_id(self, tg_id: int, **fields) -> Record:
        """
        :param tg_id: Telegram ID of the user
        :param fields: Fields to update

        :return User record
        """
        query = sql.update(User).returning(User.id).where(User.tg_id == tg_id).values(fields)
        return await pg.fetchrow(query)


class TicTacToeGameDAO(BaseDAO):
    def __init__(self):
        self.model = TicTacToeGame


class TicTacToePlayerDAO(BaseDAO):
    def __init__(self):
        self.model = TicTacToePlayer


class TicTacToeStepDAO(BaseDAO):
    def __init__(self):
        self.model = TicTacToeStep
