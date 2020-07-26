import enum

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Boolean)
from sqlalchemy.ext.declarative import as_declarative, declared_attr


class EnumSign(enum.Enum):
    cross = enum.auto()
    circle = enum.auto()


class EnumStatus(enum.Enum):
    initial = enum.auto()
    in_progress = enum.auto()
    finished = enum.auto()


@as_declarative()
class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.capitalize()

    id = Column(Integer, primary_key=True)


class User(Base):
    name = Column(String)


class TicTacToeGame(Base):
    status = Column(Enum(EnumStatus))
    current_step = Column(Integer, ForeignKey('Tictactoeplayer.id'))


class TicTacToePlayer(Base):
    user_id = Column(Integer, ForeignKey('User.id'))
    game_id = Column(Integer, ForeignKey('Tictactoegame.id'))
    sign = Column(Enum(EnumSign))
    is_winner = Column(Boolean)


class TicTacToeStep(Base):
    position = Column(Integer)
    player_id = Column(Integer, ForeignKey('Tictactoeplayer.id'))
