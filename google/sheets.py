import gspread

from google.oauth2.service_account import Credentials
from gspread.exceptions import WorksheetNotFound

from config import GOOGLE_SHEETS_ID

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

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


def append_pf_order(
    worksheet,
    order,
    reason: str = "",
):

    worksheet.append_row(
        [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),
            order.client,
            order.cpf,
            order.order,
            order.pf_amount,
            order.course_amount,
            order.dispatcher_value,
            order.operator_value,
            order.operator_name,
            order.observations or "",
            reason,
        ],
        value_input_option="USER_ENTERED",
    )


def append_pj_order(
    worksheet,
    order,
    reason: str = "",
):

    worksheet.append_row(
        [
            order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),
            order.client,
            order.cpf,
            order.order,
            order.pj_amount_cad_or_reval,
            order.pj_amount_alt_or_rem,
            order.course_amount,
            order.dispatcher_value,
            order.operator_value,
            order.operator_name,
            order.observations or "",
            reason,
        ],
        value_input_option="USER_ENTERED",
    )


def append_review_order(
    worksheet,
    order,
    category: str,
    reason: str,
):

    if category == "pf":

        worksheet.append_row(
            [
                order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),
                order.client,
                order.cpf,
                order.order,
                "PF",
                order.pf_amount,
                "",
                "",
                order.course_amount,
                order.dispatcher_value,
                order.operator_value,
                order.operator_name,
                order.observations or "",
                reason,
            ],
            value_input_option="USER_ENTERED",
        )

    elif category == "pj":

        worksheet.append_row(
            [
                order.finished_at.strftime("%d/%m/%Y %H:%M:%S"),
                order.client,
                order.cpf,
                order.order,
                "PJ",
                "",
                order.pj_amount_cad_or_reval,
                order.pj_amount_alt_or_rem,
                order.course_amount,
                order.dispatcher_value,
                order.operator_value,
                order.operator_name,
                order.observations or "",
                reason,
            ],
            value_input_option="USER_ENTERED",
        )

    else:

        raise ValueError("Categoria de pedido inválida.")


def append_order(
    order,
    category: str,
):

    worksheet_name = f"{order.guild_name}-{category}"

    worksheet = get_worksheet(worksheet_name)

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

    worksheet = spreadsheet.worksheet("revisão")

    append_review_order(
        worksheet,
        order,
        category,
        reason,
    )
