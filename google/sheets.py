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

        return spreadsheet.worksheet("revisão")


def append_row(
    worksheet,
    values,
):
    rows = worksheet.get_all_values()

    next_row = max(
        len(rows) + 1,
        3,  # cabeçalho
    )

    worksheet.update(
        f"A{next_row}:O{next_row}",
        [values],
        value_input_option="USER_ENTERED",
    )


def append_pf_order(
    worksheet,
    order,
    reason: str = "",
):

    append_row(
        worksheet,
        [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),  # 1
            order.client,  # 2
            order.document,  # 3
            order.order,  # 4
            order.pf_amount,  # 5
            order.course_amount,  # 6
            order.dispatcher_value,  # 7
            order.operator_value,  # 8
            order.operator_name,  # 9
            order.observations or "",  # 10
            "",  # 11
            "",  # 12
            "",  # 13
            reason,  # 14
            order.thread_id,  # 15
        ],
    )


def append_pj_order(
    worksheet,
    order,
    reason: str = "",
):

    append_row(
        worksheet,
        [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),  # 1
            order.client,  # 2
            order.document,  # 3
            order.order,  # 4
            order.pj_amount_cad_or_reval,  # 5
            order.pj_amount_alt_or_rem,  # 6
            order.course_amount,  # 7
            order.dispatcher_value,  # 8
            order.operator_value,  # 9
            order.operator_name,  # 10
            order.observations or "",  # 11
            "",  # 12
            "",  # 13
            reason,  # 14
            order.thread_id,  # 15
        ],
    )


def append_review_order(
    worksheet,
    order,
    category: str,
    reason: str,
):

    if category == "pf":

        append_row(
            worksheet,
            [
                order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),  # 1
                order.client,  # 2
                order.document,  # 3
                order.order,  # 4
                "PF",  # 5
                order.pf_amount,  # 6
                "",  # 7
                "",  # 8
                order.course_amount,  # 9
                order.dispatcher_value,  # 10
                order.operator_value,  # 11
                order.operator_name,  # 12
                order.observations or "",  # 13
                reason,  # 14
                order.thread_id,  # 15
            ],
        )

    elif category == "pj":

        append_row(
            worksheet,
            [
                order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),  # 1
                order.client,  # 2
                order.document,  # 3
                order.order,  # 4
                "PJ",  # 5
                "",  # 6
                order.pj_amount_cad_or_reval,  # 7
                order.pj_amount_alt_or_rem,  # 8
                order.course_amount,  # 9
                order.dispatcher_value,  # 10
                order.operator_value,  # 11
                order.operator_name,  # 12
                order.observations or "",  # 13
                reason,  # 14
                order.thread_id,  # 15
            ],
        )

    else:

        raise ValueError("Categoria de pedido inválida.")


def append_order(
    order,
    category: str,
):

    worksheet_name = f"{order.guild_name}-{category}"

    worksheet = get_worksheet(
        worksheet_name,
    )

    if worksheet.title.lower() == "revisão":

        append_review_order(
            worksheet,
            order,
            category,
            reason=f"A aba '{worksheet_name}' não existe.",
        )

        return

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

        raise ValueError("Categoria de pedido inválida.")


def append_review(
    order,
    category: str,
    reason: str,
):

    worksheet = spreadsheet.worksheet(
        "revisão",
    )

    append_review_order(
        worksheet,
        order,
        category,
        reason,
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

    worksheet_name = f"{order.guild_name}-{category}"

    worksheet = get_worksheet(
        worksheet_name,
    )

    row = find_order_row(
        worksheet,
        order.thread_id,
    )

    if row is None:

        raise ValueError(
            "Pedido não encontrado na planilha. Se o pedido tiver sido marcado como Revisão, não é possível deletá-lo da planilha, apenas manualmente.",
        )

    worksheet.delete_rows(
        row,
    )


def update_order_on_sheet(
    order,
    category: str,
):

    worksheet_name = f"{order.guild_name}-{category}"

    worksheet = get_worksheet(
        worksheet_name,
    )

    row = find_order_row(
        worksheet,
        order.thread_id,
    )

    if row is None:

        raise ValueError(
            "Pedido não encontrado na planilha. Se o pedido tiver sido marcado como Revisão, não é possível alterá-lo na planilha, apenas manualmente. Procure um administrador.",
        )

    if category == "pf":

        values = [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),  # A
            order.client,  # B
            order.document,  # C
            order.order,  # D
            order.pf_amount,  # E
            order.course_amount,  # F
            order.dispatcher_value,  # G
            order.operator_value,  # H
            order.operator_name,  # I
            order.observations or "",  # J
            "",  # K
            "",  # L
            "",  # M
            "",  # N
            order.thread_id,  # O
        ]

    elif category == "pj":

        values = [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),  # A
            order.client,  # B
            order.document,  # C
            order.order,  # D
            order.pj_amount_cad_or_reval,  # E
            order.pj_amount_alt_or_rem,  # F
            order.course_amount,  # G
            order.dispatcher_value,  # H
            order.operator_value,  # I
            order.operator_name,  # J
            order.observations or "",  # K
            "",  # L
            "",  # M
            "",  # N
            order.thread_id,  # O
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
