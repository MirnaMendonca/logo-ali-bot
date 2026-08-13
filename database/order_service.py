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


def calculate_order_values(
    order: Order,
):

    guild = GUILDS.get(
        int(order.guild_id),
    )

    if guild is None:
        raise ValueError("Este servidor não possui configuração.")

    if order.category == "pf":

        pf_price = guild["pf_price"]

        order.dispatcher_value = (pf_price * order.pf_amount) + (
            COURSE_PRICE * order.course_amount
        )

        order.operator_value = (PF_OPERATOR_VALUE * order.pf_amount) + (
            COURSE_PRICE * order.course_amount
        )

    elif order.category == "pj":

        order.dispatcher_value = (
            (PJ_REFUND_VALUE_CAD_OR_REVAL * order.pj_amount_cad_or_reval)
            + (PJ_REFUND_VALUE_ALT_OR_REM * order.pj_amount_alt_or_rem)
            + (COURSE_PRICE * order.course_amount)
        )

        order.operator_value = (
            (PJ_OPERATOR_VALUE_CAD_OR_REVAL * order.pj_amount_cad_or_reval)
            + (PJ_OPERATOR_VALUE_ALT_OR_REM * order.pj_amount_alt_or_rem)
            + (COURSE_PRICE * order.course_amount)
        )

    else:

        raise ValueError("Categoria de pedido inválida.")


def create_order(
    *,
    thread_id: str,
    guild_id: str,
    operator_discord_id: str,
    client: str,
    document: str,
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

        guild = GUILDS.get(
            int(guild_id),
        )

        if guild is None:
            raise ValueError("Este servidor não possui configuração.")

        if order_category not in ("pf", "pj"):
            raise ValueError("Categoria de pedido inválida.")

        finished_at = datetime.now(
            timezone(
                timedelta(hours=-3),
            )
        )

        new_order = Order(
            thread_id=thread_id,
            guild_id=guild_id,
            guild_name=guild["dispatcher_name"],
            operator_id=operator.id,
            operator_name=operator.name,
            category=order_category,
            client=client,
            document=document,
            order=order,
            pf_amount=pf_amount,
            course_amount=course_amount,
            pj_amount_cad_or_reval=pj_amount_cad_or_reval,
            pj_amount_alt_or_rem=pj_amount_alt_or_rem,
            observations=observations,
            finished_at=finished_at,
        )

        calculate_order_values(
            new_order,
        )

        session.add(
            new_order,
        )

        session.commit()

        session.refresh(
            new_order,
        )

        return new_order

    except:

        session.rollback()
        raise

    finally:

        session.close()


def get_order_by_thread_id(
    *,
    session,
    thread_id: str,
) -> Order | None:

    return (
        session.query(Order)
        .filter_by(
            thread_id=thread_id,
        )
        .first()
    )


def delete_order(
    *,
    session,
    thread_id: str,
) -> Order:

    order = get_order_by_thread_id(
        session=session,
        thread_id=thread_id,
    )

    if order is None:
        raise ValueError("Pedido não encontrado.")

    session.delete(
        order,
    )

    return order


def edit_order(
    *,
    session,
    thread_id: str,
    client: str | None = None,
    document: str | None = None,
    order_text: str | None = None,
    pf_amount: int | None = None,
    pj_amount_cad_or_reval: int | None = None,
    pj_amount_alt_or_rem: int | None = None,
    course_amount: int | None = None,
    operator_discord_id: str | None = None,
    observations: str | None = None,
) -> Order:

    order = get_order_by_thread_id(
        session=session,
        thread_id=thread_id,
    )

    if order is None:
        raise ValueError("Pedido não encontrado.")

    if client is not None:
        order.client = client

    if document is not None:
        order.document = document

    if order_text is not None:
        order.order = order_text

    if order.category == "pf":

        if pf_amount is not None:
            order.pf_amount = pf_amount

    elif order.category == "pj":

        if pj_amount_cad_or_reval is not None:
            order.pj_amount_cad_or_reval = pj_amount_cad_or_reval

        if pj_amount_alt_or_rem is not None:
            order.pj_amount_alt_or_rem = pj_amount_alt_or_rem

    else:

        raise ValueError("Categoria de pedido inválida.")

    if course_amount is not None:
        order.course_amount = course_amount

    if observations is not None:
        order.observations = observations

    if operator_discord_id is not None:

        operator = (
            session.query(User)
            .filter_by(
                discord_id=operator_discord_id,
            )
            .first()
        )

        if operator is None:
            raise ValueError("Operador não cadastrado.")

        order.operator_id = operator.id
        order.operator_name = operator.name

    calculate_order_values(
        order,
    )

    return order
