from io import BytesIO
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
import warnings

from openpyxl import Workbook, load_workbook

from database.reports import get_orders


def _parse_order_amount(value: object, row_number: int, worksheet_name: str) -> Decimal:
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))

    if isinstance(value, str):
        normalized_value = value.strip()
        if "," in normalized_value:
            normalized_value = normalized_value.replace(".", "").replace(",", ".")
        try:
            return Decimal(normalized_value)
        except InvalidOperation as error:
            raise ValueError(
                f"Valor total inválido na linha {row_number} da aba "
                f"'{worksheet_name}'."
            ) from error

    raise ValueError(
        f"Valor total inválido na linha {row_number} da aba '{worksheet_name}'."
    )


def summarize_orders_by_operator(
    file_content: bytes,
) -> tuple[
    dict[date, dict[str, dict[str, int]]],
    dict[str, dict[str, int]],
]:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="^Workbook contains no default style, apply openpyxl's default$",
            category=UserWarning,
            module=r"openpyxl\.styles\.stylesheet",
        )
        workbook = load_workbook(
            BytesIO(file_content),
            read_only=True,
            data_only=True,
        )

    try:
        if not workbook.worksheets:
            raise ValueError("A planilha não contém abas.")

        worksheet = workbook.worksheets[0]
        daily_counts: defaultdict[date, defaultdict[str, Counter[str]]] = defaultdict(
            lambda: defaultdict(Counter)
        )
        totals: defaultdict[str, Counter[str]] = defaultdict(Counter)

        for row_number, row in enumerate(
            worksheet.iter_rows(
                min_row=9,
                values_only=True,
            ),
            start=9,
        ):
            order_date = row[2] if len(row) > 2 else None
            operator = row[6] if len(row) > 6 else None
            order_amount = row[15] if len(row) > 15 else None

            if order_date is None and operator is None:
                continue
            if (
                order_date is None
                or not isinstance(operator, str)
                or not operator.strip()
            ):
                raise ValueError(
                    f"Registro incompleto na linha {row_number} da aba "
                    f"'{worksheet.title}'."
                )

            if isinstance(order_date, datetime):
                parsed_date = order_date.date()
            elif isinstance(order_date, date):
                parsed_date = order_date
            elif isinstance(order_date, str):
                try:
                    parsed_date = datetime.strptime(
                        order_date.strip(),
                        "%d/%m/%Y",
                    ).date()
                except ValueError as error:
                    raise ValueError(
                        f"Data inválida na linha {row_number} da aba "
                        f"'{worksheet.title}'."
                    ) from error
            else:
                raise ValueError(
                    f"Data inválida na linha {row_number} da aba "
                    f"'{worksheet.title}'."
                )

            operator_name = operator.strip()
            amount = _parse_order_amount(order_amount, row_number, worksheet.title)
            category = "free" if amount == 0 else "paid"
            daily_counts[parsed_date][operator_name][category] += 1
            totals[operator_name][category] += 1

        return (
            {
                day: {
                    operator: dict(counts)
                    for operator, counts in operator_counts.items()
                }
                for day, operator_counts in sorted(daily_counts.items())
            },
            {operator: dict(counts) for operator, counts in totals.items()},
        )
    finally:
        workbook.close()


def format_operator_summary(
    daily_counts: dict[date, dict[str, dict[str, int]]],
    totals: dict[str, dict[str, int]],
) -> str:
    if not daily_counts:
        return "Não encontrei pedidos válidos nessa planilha."

    period = (
        f"{min(daily_counts).strftime('%d/%m/%Y')} a "
        f"{max(daily_counts).strftime('%d/%m/%Y')}"
    )
    lines = [
        "Resumo de pedidos por operador",
        f"Período: {period}",
    ]

    first_day = min(daily_counts)
    last_day = max(daily_counts)
    for operator, total in sorted(
        totals.items(),
        key=lambda item: (
            -(item[1].get("paid", 0) + item[1].get("free", 0)),
            item[0].casefold(),
        ),
    ):
        lines.append(f"\n{operator}:")
        day = first_day
        while day <= last_day:
            counts = daily_counts.get(day, {}).get(operator, {})
            paid = counts.get("paid", 0)
            free = counts.get("free", 0)
            lines.append(
                f"- {day.strftime('%d/%m/%Y')}: " f"{paid} com valor | {free} gratuitos"
            )
            day += timedelta(days=1)

    lines.append("\nTOTAIS")
    for operator, counts in sorted(
        totals.items(),
        key=lambda item: (
            -(item[1].get("paid", 0) + item[1].get("free", 0)),
            item[0].casefold(),
        ),
    ):
        paid = counts.get("paid", 0)
        free = counts.get("free", 0)
        lines.append(
            f"- {operator}: {paid} com valor | {free} gratuitos "
            f"| {paid + free} pedidos"
        )

    return "\n".join(lines)


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
