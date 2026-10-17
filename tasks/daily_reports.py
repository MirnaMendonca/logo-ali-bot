from datetime import datetime, timezone, timedelta
import asyncio
import os

import discord

from config import GUILDS
from database.reports import get_daily_closing_period
from database.reports import get_general_summary
from utils.excel import generate_daily_excel

LAST_SENT_DATE = {}

BRASIL = timezone(
    timedelta(hours=-3),
)

DAILY_REPORT_EMBED_TITLE = "📊 Fechamento diário"


async def _has_daily_report_message(
    channel: discord.TextChannel,
    guild: discord.Guild,
    *,
    after: datetime,
    embed_title: str | None = None,
    attachment_name: str | None = None,
):
    bot_member = guild.me

    if bot_member is None:
        raise RuntimeError("Bot não encontrado no servidor.")

    async for message in channel.history(
        limit=100,
        after=after,
    ):
        if message.author.id != bot_member.id:
            continue

        if embed_title is not None and any(
            embed.title == embed_title for embed in message.embeds
        ):
            return True

        if attachment_name is not None and any(
            attachment.filename == attachment_name for attachment in message.attachments
        ):
            return True

    return False


async def send_daily_report(
    guild: discord.Guild,
    date: datetime | None = None,
    *,
    skip_existing: bool = False,
):

    if date is None:
        date = datetime.now(BRASIL)

    today = date.date()
    day_start = datetime(
        today.year,
        today.month,
        today.day,
        tzinfo=BRASIL,
    )
    start_date, end_date = get_daily_closing_period(date)

    channel = discord.utils.get(
        guild.text_channels,
        name="relatorio-financeiro",
    )

    if channel is None:
        raise ValueError(
            "Canal 'relatorio-financeiro' não encontrado.",
        )

    summary = get_general_summary(
        guild_id=str(guild.id),
        start_date=start_date,
        end_date=end_date,
    )

    dispatcher = summary["dispatcher"]

    embed = discord.Embed(
        title=DAILY_REPORT_EMBED_TITLE,
        color=discord.Color.green(),
    )

    embed.add_field(
        name="PF",
        value=(
            f"Taxas: {dispatcher['pf_amount']}\n"
            f"Exclusões PJ: {dispatcher['pf_exclusions_pj']}\n"
            f"Desconto: R$ {dispatcher['pf_discount_value']:.2f}\n"
            f"Valor: R$ {dispatcher['pf_value']:.2f}"
        ),
        inline=False,
    )

    embed.add_field(
        name="PJ",
        value=(
            f"Cadastros/Reativações/Inclusões: "
            f"{dispatcher['pj_amount_cad_or_reval']}\n"
            f"Alterações/Remoções: "
            f"{dispatcher['pj_amount_alt_or_rem']}\n"
            f"Valor: R$ {dispatcher['pj_refund_value']:.2f}"
        ),
        inline=False,
    )

    embed.add_field(
        name="Cursos",
        value=(
            f"Quantidade: {dispatcher['course_amount']}\n"
            f"Valor: R$ {dispatcher['course_value']:.2f}"
        ),
        inline=False,
    )

    embed.add_field(
        name="Total a cobrar",
        value=f"R$ {dispatcher['net_value']:.2f}",
        inline=False,
    )

    #
    # Sexta-feira (weekday = 4)
    #

    if date.weekday() == 4:

        operators_text = ""

        for operator in summary["operators"]:

            operators_text += (
                f"**{operator['name']}**\n"
                f"Pedidos: {operator['orders']}\n"
                f"Receber: R$ {operator['value']:.2f}\n\n"
            )

        if not operators_text:

            operators_text = "Nenhum pedido nesta semana."

        embed.add_field(
            name="💰 Pagamentos da semana",
            value=operators_text,
            inline=False,
        )

        embed.add_field(
            name="Total a pagar",
            value=f"R$ {summary['operators_total']:.2f}",
            inline=False,
        )

    if not skip_existing or not await _has_daily_report_message(
        channel,
        guild,
        after=day_start,
        embed_title=DAILY_REPORT_EMBED_TITLE,
    ):
        await channel.send(
            embed=embed,
        )

    #
    # Planilha dos pedidos do dia
    #

    order_reports_channel = discord.utils.get(
        guild.text_channels,
        name="relatorio-pedidos",
    )

    if order_reports_channel is None:
        raise ValueError(
            "Canal 'relatorio-pedidos' não encontrado.",
        )

    attachment_name = f"fechamento-{guild.id}-{end_date.strftime('%Y-%m-%d')}.xlsx"

    if skip_existing and await _has_daily_report_message(
        order_reports_channel,
        guild,
        after=day_start,
        attachment_name=attachment_name,
    ):
        return

    excel_path = generate_daily_excel(
        guild_id=str(guild.id),
        start_date=start_date,
        end_date=end_date,
    )

    try:
        await order_reports_channel.send(
            content=(
                f"📄 **Pedidos do fechamento de "
                f"{today.strftime('%d/%m/%Y')} "
                f"(20h do dia anterior até 20h de hoje):**"
            ),
            file=discord.File(excel_path),
        )
    finally:
        if os.path.exists(excel_path):
            os.remove(excel_path)


async def send_daily_reports(
    bot: discord.Client,
):

    await bot.wait_until_ready()

    while not bot.is_closed():

        now = datetime.now(BRASIL)

        if now.hour >= 20:

            today = now.date()

            for guild in bot.guilds:
                if guild.id not in GUILDS:
                    continue

                if LAST_SENT_DATE.get(guild.id) == today:
                    continue

                try:

                    await send_daily_report(
                        guild=guild,
                        date=now,
                        skip_existing=True,
                    )

                    LAST_SENT_DATE[guild.id] = today

                except Exception as e:

                    print(f"Erro ao enviar relatório de " f"{guild.name}: {e}")

        #
        # Verifica o horário do fechamento a cada minuto.
        #

        await asyncio.sleep(60)
