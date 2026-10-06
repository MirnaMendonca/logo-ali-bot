from pathlib import Path
from datetime import datetime

from openpyxl import Workbook

from database.reports import get_orders


def generate_daily_excel(
    *,
    guild_id: str,
    start_date: datetime,
    end_date: datetime,
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
            "Valor",
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
            "Valor",
            "Operador",
            "Observações",
        ]
    )

    orders = get_orders(
        guild_id=guild_id,
        start_date=start_date,
        end_date=end_date,
    )

    for order in orders:

        if order.category == "pf":

            pf_sheet.append(
                [
                    order.finished_at.strftime("%d/%m/%Y %H:%M"),
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

        elif order.category == "pj":

            pj_sheet.append(
                [
                    order.finished_at.strftime("%d/%m/%Y %H:%M"),
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
        / f"fechamento-{guild_id}-{end_date.strftime('%Y-%m-%d')}.xlsx"
    )

    workbook.save(
        filename,
    )

    workbook.close()

    return str(
        filename,
    )
