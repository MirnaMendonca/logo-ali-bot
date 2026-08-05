from datetime import datetime, timezone, timedelta
import asyncio
import os

import discord

from database.reports import get_general_summary
from utils.excel import generate_daily_excel

LAST_SENT_DATE = {}

BRASIL = timezone(
    timedelta(hours=-3),
)


async def send_daily_reports(bot: discord.Client):

    await bot.wait_until_ready()

    while not bot.is_closed():

        now = datetime.now(BRASIL)

        if now.hour == 23:

            today = now.date()

            for guild in bot.guilds:

                if LAST_SENT_DATE.get(guild.id) == today:
                    continue

                channel = discord.utils.get(
                    guild.text_channels,
                    name="relatorio-financeiro",
                )

                if channel is None:
                    continue

                try:

                    summary = get_general_summary(
                        guild_id=str(guild.id),
                    )

                    dispatcher = summary["dispatcher"]

                    embed = discord.Embed(
                        title="📊 Fechamento diário",
                        color=discord.Color.green(),
                    )

                    embed.add_field(
                        name="PF",
                        value=(
                            f"Taxas: {dispatcher['pf_amount']}\n"
                            f"Valor: R$ {dispatcher['pf_value']:.2f}"
                        ),
                        inline=False,
                    )

                    embed.add_field(
                        name="PJ",
                        value=(
                            f"Cadastros/Reativações/Inclusões: {dispatcher['pj_amount_cad_or_reval']}\n"
                            f"Alterações/Remoções: {dispatcher['pj_amount_alt_or_rem']}\n"
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

                    if now.weekday() == 4:

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

                    excel_path = generate_daily_excel(
                        guild_id=str(guild.id),
                        date=now,
                    )

                    await order_reports_channel.send(
                        content=f"📄 **Pedidos do dia {today.strftime('%d/%m/%Y')}:**",
                        file=discord.File(excel_path),
                    )

                    os.remove(excel_path)

                    LAST_SENT_DATE[guild.id] = today

                except Exception as e:

                    print(f"Erro ao enviar relatório de {guild.name}: {e}")

        #
        # Dorme uma hora
        #

        await asyncio.sleep(3600)
