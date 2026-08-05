from pathlib import Path
from datetime import datetime

from openpyxl import Workbook

from database.reports import get_orders


def generate_daily_excel(
    *,
    guild_id: str,
    date: datetime,
) -> str:

    workbook = Workbook()

    pf_sheet = workbook.active
    pf_sheet.title = "PF"

    pj_sheet = workbook.create_sheet(
        "PJ",
    )

    pf_sheet.append(
        [
            "Data",
            "Cliente",
            "CPF",
            "Pedidos",
            "Qtd. Taxas",
            "Cursos",
            "Valor a cobrar",
            "Operador",
            "Observações",
        ]
    )

    pj_sheet.append(
        [
            "Data",
            "Cliente",
            "CNPJ",
            "Pedidos",
            "Cadastros/Reativações",
            "Alterações/Exclusões",
            "Cursos",
            "Valor a cobrar",
            "Operador",
            "Observações",
        ]
    )

    start = datetime(
        date.year,
        date.month,
        date.day,
    )

    end = start.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    from datetime import timedelta

    end += timedelta(
        days=1,
    )

    orders = get_orders(
        guild_id=guild_id,
        start_date=start,
        end_date=end,
    )

    for order in orders:

        if order.pf_amount > 0:

            pf_sheet.append(
                [
                    order.finished_at.strftime(
                        "%d/%m/%Y %H:%M",
                    ),
                    order.client,
                    order.document,
                    order.order,
                    order.pf_amount,
                    order.course_amount,
                    order.dispatcher_value,
                    order.operator_name,
                    order.observations or "",
                ]
            )

        else:

            pj_sheet.append(
                [
                    order.finished_at.strftime(
                        "%d/%m/%Y %H:%M",
                    ),
                    order.client,
                    order.document,
                    order.order,
                    order.pj_amount_cad_or_reval,
                    order.pj_amount_alt_or_rem,
                    order.course_amount,
                    order.dispatcher_value,
                    order.operator_name,
                    order.observations or "",
                ]
            )

    filename = (
        Path(__file__).parent
        / f"fechamento-{guild_id}-{date.strftime('%Y-%m-%d')}.xlsx"
    )

    workbook.save(
        filename,
    )

    workbook.close()

    return str(
        filename,
    )
