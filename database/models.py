from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    discord_id = Column(
        String,
        unique=True,
        nullable=False,
    )

    name = Column(
        String,
        nullable=False,
    )

    role = Column(
        String,
        nullable=False,
    )


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)

    thread_id = Column(
        String,
        unique=True,
        nullable=False,
    )

    guild_id = Column(
        String,
        nullable=False,
    )

    guild_name = Column(
        String,
        nullable=False,
    )

    operator_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    operator_name = Column(
        String,
        nullable=False,
    )

    category = Column(
        String,
        nullable=False,
    )

    client = Column(
        String,
        nullable=False,
    )

    document = Column(
        String,
        nullable=False,
    )

    order = Column(
        String,
        nullable=False,
    )

    pf_amount = Column(
        Integer,
        default=0,
        nullable=False,
    )

    pj_amount_cad_or_reval = Column(
        Integer,
        default=0,
        nullable=False,
    )

    pj_amount_alt_or_rem = Column(
        Integer,
        default=0,
        nullable=False,
    )

    course_amount = Column(
        Integer,
        default=0,
        nullable=False,
    )

    dispatcher_value = Column(
        Float,
        nullable=False,
    )

    operator_value = Column(
        Float,
        nullable=False,
    )

    observations = Column(
        String,
        nullable=True,
    )

    finished_at = Column(DateTime, nullable=False)
