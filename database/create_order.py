from datetime import datetime, timezone, timedelta

from database.database import SessionLocal
from database.models import Order
from database.models import User

from config import (
    GUILDS,
    COURSE_PRICE,
    PF_OPERATOR_VALUE,
    PJ_OPERATOR_VALUE_ALT_OR_REM,
    PJ_OPERATOR_VALUE_CAD_OR_REVAL,
    PJ_REFUND_VALUE_CAD_OR_REVAL,
    PJ_REFUND_VALUE_ALT_OR_REM,
)


def create_order(
    *,
    guild_id: str,
    operator_discord_id: str,
    client: str,
    cpf: str,
    order: str,
    order_category: str,
    pf_amount: int = 0,
    course_amount: int = 0,
    pj_amount_cad_or_reval: int = 0,
    pj_amount_alt_or_rem: int = 0,
    observations: str | None = None,
) -> Order:

    session = SessionLocal()

    try:

        operator = (
            session.query(User)
            .filter_by(
                discord_id=operator_discord_id,
            )
            .first()
        )

        if operator is None:
            raise ValueError("Operador não cadastrado.")

        guild = GUILDS.get(int(guild_id))

        if guild is None:
            raise ValueError("Este servidor não possui configuração.")

        guild_name = guild["dispatcher_name"]

        dispatcher_value = 0
        operator_value = 0

        if order_category == "pf":

            pf_price = guild["pf_price"]

            dispatcher_value = (pf_price * pf_amount) + (COURSE_PRICE * course_amount)

            operator_value = (PF_OPERATOR_VALUE * pf_amount) + (
                COURSE_PRICE * course_amount
            )

        elif order_category == "pj":

            dispatcher_value = (
                (PJ_REFUND_VALUE_CAD_OR_REVAL * pj_amount_cad_or_reval)
                + (PJ_REFUND_VALUE_ALT_OR_REM * pj_amount_alt_or_rem)
                + (COURSE_PRICE * course_amount)
            )

            operator_value = (
                (PJ_OPERATOR_VALUE_CAD_OR_REVAL * pj_amount_cad_or_reval)
                + (PJ_OPERATOR_VALUE_ALT_OR_REM * pj_amount_alt_or_rem)
                + (COURSE_PRICE * course_amount)
            )

        else:

            raise ValueError("Categoria de pedido inválida.")

        finished_at = datetime.now(timezone(timedelta(hours=-3)))

        order = Order(
            guild_id=guild_id,
            guild_name=guild_name,
            operator_id=operator.id,
            operator_name=operator.name,
            client=client,
            cpf=cpf,
            order=order,
            pf_amount=pf_amount,
            course_amount=course_amount,
            pj_amount_cad_or_reval=pj_amount_cad_or_reval,
            pj_amount_alt_or_rem=pj_amount_alt_or_rem,
            dispatcher_value=dispatcher_value,
            operator_value=operator_value,
            observations=observations,
            finished_at=finished_at,
        )

        session.add(order)
        session.commit()
        session.refresh(order)

        return order

    except:

        session.rollback()
        raise

    finally:

        session.close()
