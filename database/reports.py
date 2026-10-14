from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone

from sqlalchemy import func

from database.database import SessionLocal
from database.models import Order
from database.models import User

from config import (
    COURSE_PRICE,
    GUILDS,
    PJ_REFUND_VALUE_ALT_OR_REM,
    PJ_REFUND_VALUE_CAD_OR_REVAL,
)

BRASIL = timezone(
    timedelta(hours=-3),
)

DAILY_CLOSING_HOUR = 20


def start_of_today():

    now = datetime.now(BRASIL)

    return datetime(
        now.year,
        now.month,
        now.day,
    )


def get_daily_closing_period(
    date: datetime,
):

    end = datetime(
        date.year,
        date.month,
        date.day,
        DAILY_CLOSING_HOUR,
    )

    return end - timedelta(days=1), end


def start_of_month():

    today = start_of_today()

    return datetime(
        today.year,
        today.month,
        1,
    )


def start_of_payment_week():

    today = start_of_today()

    #
    # Semana de pagamento:
    # sábado -> sexta
    #

    days_since_saturday = (today.weekday() + 2) % 7

    return today - timedelta(
        days=days_since_saturday,
    )


def get_operator_summary(
    operator_discord_id: str,
    start_date: datetime,
    end_date: datetime | None = None,
):

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

        query = session.query(
            func.count(Order.id),
            func.sum(Order.operator_value),
        ).filter(
            Order.operator_id == operator.id,
            Order.finished_at >= start_date,
        )

        if end_date is not None:

            query = query.filter(
                Order.finished_at < end_date,
            )

        orders, value = query.one()

        return {
            "orders": orders or 0,
            "value": value or 0,
        }

    finally:

        session.close()


def get_dispatcher_summary(
    guild_id: str,
    start_date: datetime,
    end_date: datetime | None = None,
):

    session = SessionLocal()

    try:

        guild = GUILDS.get(int(guild_id))

        if guild is None:
            raise ValueError("Servidor não configurado.")

        pf_price = guild["pf_price"]

        query = session.query(
            func.sum(Order.pf_amount),
            func.sum(Order.pf_exclusions_pj),
            func.sum(Order.pj_amount_cad_or_reval),
            func.sum(Order.pj_amount_alt_or_rem),
            func.sum(Order.course_amount),
        ).filter(
            Order.guild_id == guild_id,
            Order.finished_at >= start_date,
        )

        if end_date is not None:

            query = query.filter(
                Order.finished_at < end_date,
            )

        (
            pf_amount,
            pf_exclusions_pj,
            pj_amount_cad_or_reval,
            pj_amount_alt_or_rem,
            course_amount,
        ) = query.one()

        pf_amount = pf_amount or 0
        pf_exclusions_pj = pf_exclusions_pj or 0
        pj_amount_cad_or_reval = pj_amount_cad_or_reval or 0
        pj_amount_alt_or_rem = pj_amount_alt_or_rem or 0
        course_amount = course_amount or 0

        pf_exclusion_discount = pf_exclusions_pj * PJ_REFUND_VALUE_ALT_OR_REM
        pf_value = (pf_amount * pf_price) - pf_exclusion_discount
        course_value = course_amount * COURSE_PRICE

        pj_refund_value = (pj_amount_cad_or_reval * PJ_REFUND_VALUE_CAD_OR_REVAL) + (
            pj_amount_alt_or_rem * PJ_REFUND_VALUE_ALT_OR_REM
        )

        return {
            "pf_amount": pf_amount,
            "pf_exclusions_pj": pf_exclusions_pj,
            "pj_amount_cad_or_reval": pj_amount_cad_or_reval,
            "pj_amount_alt_or_rem": pj_amount_alt_or_rem,
            "course_amount": course_amount,
            "pf_value": pf_value,
            "pf_discount_value": pf_exclusion_discount,
            "course_value": course_value,
            "pj_refund_value": pj_refund_value,
            "net_value": (pf_value + course_value - pj_refund_value),
        }

    finally:

        session.close()


def get_general_summary(
    guild_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):

    session = SessionLocal()

    try:

        dispatcher = get_dispatcher_summary(
            guild_id=guild_id,
            start_date=start_date or start_of_today(),
            end_date=end_date,
        )

        week_start = start_of_payment_week()

        operators_query = (
            session.query(
                User.name,
                func.count(Order.id),
                func.sum(Order.operator_value),
            )
            .join(
                Order,
                Order.operator_id == User.id,
            )
            .filter(
                Order.guild_id == guild_id,
                Order.finished_at >= week_start,
            )
            .group_by(
                User.id,
                User.name,
            )
            .order_by(
                User.name,
            )
        )

        operators = []

        operators_total = 0

        for (
            name,
            orders,
            value,
        ) in operators_query.all():

            value = value or 0

            operators.append(
                {
                    "name": name,
                    "orders": orders or 0,
                    "value": value,
                }
            )

            operators_total += value

        return {
            "dispatcher": dispatcher,
            "operators": operators,
            "operators_total": operators_total,
            "payment_week_start": week_start,
        }

    finally:

        session.close()


def get_orders(
    guild_id: str,
    start_date: datetime,
    end_date: datetime | None = None,
):

    session = SessionLocal()

    try:

        query = (
            session.query(Order)
            .filter(
                Order.guild_id == guild_id,
                Order.finished_at >= start_date,
            )
            .order_by(
                Order.finished_at.asc(),
            )
        )

        if end_date is not None:

            query = query.filter(
                Order.finished_at < end_date,
            )

        return query.all()

    finally:

        session.close()


def get_order_counts_by_day(
    guild_id: str,
    start_date: date,
    end_date: date,
) -> dict[date, int]:
    session = SessionLocal()

    try:
        start = datetime.combine(start_date, datetime.min.time())
        end = datetime.combine(end_date + timedelta(days=1), datetime.min.time())

        finished_dates = (
            session.query(Order.finished_at)
            .filter(
                Order.guild_id == guild_id,
                Order.finished_at >= start,
                Order.finished_at < end,
            )
            .all()
        )

        counts: dict[date, int] = {}
        for (finished_at,) in finished_dates:
            finished_day = finished_at.date()
            counts[finished_day] = counts.get(finished_day, 0) + 1

        return counts
    finally:
        session.close()


def get_today_period():

    start = start_of_today()

    return start, None


def get_month_period():

    start = start_of_month()

    return start, None


def get_payment_week_period():

    start = start_of_payment_week()

    return start, None


def get_custom_period(
    start_date: datetime,
    end_date: datetime,
):

    start = datetime(
        start_date.year,
        start_date.month,
        start_date.day,
    )

    end = datetime(
        end_date.year,
        end_date.month,
        end_date.day,
    ) + timedelta(days=1)

    return start, end
