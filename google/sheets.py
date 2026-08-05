import gspread

from google.oauth2.service_account import Credentials
from gspread.exceptions import WorksheetNotFound

from config import GOOGLE_SHEETS_ID

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

THREAD_ID_COLUMN = 15

credentials = Credentials.from_service_account_file(
    "logoali-bot-6a807097c60f.json",
    scopes=SCOPES,
)

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(GOOGLE_SHEETS_ID)


def get_worksheet(name: str):

    try:

        return spreadsheet.worksheet(name)

    except WorksheetNotFound:

        raise ValueError(
            f"A aba '{name}' não foi encontrada na planilha.",
        )


def append_row(
    worksheet,
    values,
):

    rows = worksheet.get_all_values()

    next_row = max(
        len(rows) + 1,
        3,
    )

    worksheet.update(
        f"A{next_row}:O{next_row}",
        [values],
        value_input_option="USER_ENTERED",
    )


def append_pf_order(
    worksheet,
    order,
):

    append_row(
        worksheet,
        [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),
            order.client,
            order.document,
            order.order,
            order.pf_amount,
            order.course_amount,
            order.dispatcher_value,
            order.operator_value,
            order.operator_name,
            order.observations or "",
            "",
            "",
            "",
            "",
            order.thread_id,
        ],
    )


def append_pj_order(
    worksheet,
    order,
):

    append_row(
        worksheet,
        [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),
            order.client,
            order.document,
            order.order,
            order.pj_amount_cad_or_reval,
            order.pj_amount_alt_or_rem,
            order.course_amount,
            order.dispatcher_value,
            order.operator_value,
            order.operator_name,
            order.observations or "",
            "",
            "",
            "",
            order.thread_id,
        ],
    )


def append_order(
    order,
    category: str,
):

    worksheet = get_worksheet(
        f"{order.guild_name}-{category}",
    )

    if category == "pf":

        append_pf_order(
            worksheet,
            order,
        )

    elif category == "pj":

        append_pj_order(
            worksheet,
            order,
        )

    else:

        raise ValueError(
            "Categoria de pedido inválida.",
        )


def find_order_row(
    worksheet,
    thread_id: str,
) -> int | None:

    values = worksheet.col_values(
        THREAD_ID_COLUMN,
    )

    for index, value in enumerate(
        values,
        start=1,
    ):

        if value == thread_id:

            return index

    return None


def delete_order_from_sheet(
    order,
    category: str,
):

    worksheet = get_worksheet(
        f"{order.guild_name}-{category}",
    )

    row = find_order_row(
        worksheet,
        order.thread_id,
    )

    if row is None:

        raise ValueError(
            "Pedido não encontrado na planilha.",
        )

    worksheet.delete_rows(
        row,
    )


def update_order_on_sheet(
    order,
    category: str,
):

    worksheet = get_worksheet(
        f"{order.guild_name}-{category}",
    )

    row = find_order_row(
        worksheet,
        order.thread_id,
    )

    if row is None:

        raise ValueError(
            "Pedido não encontrado na planilha.",
        )

    if category == "pf":

        values = [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),
            order.client,
            order.document,
            order.order,
            order.pf_amount,
            order.course_amount,
            order.dispatcher_value,
            order.operator_value,
            order.operator_name,
            order.observations or "",
            "",
            "",
            "",
            "",
            order.thread_id,
        ]

    elif category == "pj":

        values = [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),
            order.client,
            order.document,
            order.order,
            order.pj_amount_cad_or_reval,
            order.pj_amount_alt_or_rem,
            order.course_amount,
            order.dispatcher_value,
            order.operator_value,
            order.operator_name,
            order.observations or "",
            "",
            "",
            "",
            order.thread_id,
        ]

    else:

        raise ValueError(
            "Categoria de pedido inválida.",
        )

    worksheet.update(
        f"A{row}:O{row}",
        [values],
        value_input_option="USER_ENTERED",
    )
