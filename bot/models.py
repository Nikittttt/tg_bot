import enum
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
    Boolean,
    DateTime
)
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import relationship


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
        return cls.__name__

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now, server_default='NOW()')


class User(Base):
    tg_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)


class TicTacToeGame(Base):
    status = Column(Enum(EnumStatus), nullable=False, default=EnumStatus.initial)
    current_step_user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    current_step_user = relationship('User')


class TicTacToePlayer(Base):
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)
    user = relationship('User')
    game_id = Column(Integer, ForeignKey('TicTacToeGame.id'), nullable=False)
    game = relationship('TicTacToeGame')
    sign = Column(Enum(EnumSign))
    is_winner = Column(Boolean)


class TicTacToeStep(Base):
    position = Column(Integer, nullable=False)
    player_id = Column(Integer, ForeignKey('TicTacToePlayer.id'), nullable=False)
    player = relationship('TicTacToePlayer')
