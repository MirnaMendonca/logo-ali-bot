from datetime import datetime

import discord
from discord import app_commands

from database.reports import (
    get_operator_summary,
    get_today_period,
    get_month_period,
    get_custom_period,
)

from config import USER_ROLES


async def send_operator_report(
    interaction: discord.Interaction,
    *,
    period: str,
    start_date_value: str | None = None,
    end_date_value: str | None = None,
):
    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "Este relatório só pode ser consultado dentro de um servidor.",
            ephemeral=True,
        )
        return

    operator_role = discord.utils.get(
        guild.roles,
        name=USER_ROLES["operator"],
    )
    if (
        operator_role is None
        or not isinstance(interaction.user, discord.Member)
        or operator_role not in interaction.user.roles
    ):
        await interaction.response.send_message(
            "Apenas operadores podem utilizar este relatório.",
            ephemeral=True,
        )
        return

    try:
        if period == "today":
            start, end = get_today_period()
        elif period == "month":
            start, end = get_month_period()
        elif period == "custom":
            if start_date_value is None or end_date_value is None:
                raise ValueError("Informe a data inicial e a data final.")

            start_date = datetime.strptime(start_date_value, "%d/%m/%Y")
            end_date = datetime.strptime(end_date_value, "%d/%m/%Y")
            start, end = get_custom_period(start_date, end_date)
        else:
            raise ValueError("Período de relatório inválido.")

        summary = get_operator_summary(
            operator_discord_id=str(interaction.user.id),
            start_date=start,
            end_date=end,
        )
    except ValueError as error:
        await interaction.response.send_message(
            str(error),
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title="📊 Relatório do operador",
        color=discord.Color.blue(),
    )
    embed.add_field(
        name="Pedidos finalizados",
        value=str(summary["orders"]),
        inline=False,
    )
    embed.add_field(
        name="Valor",
        value=f"R$ {summary['value']:.2f}",
        inline=False,
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )


def setup_report_operator(bot: discord.Client):

    @bot.tree.command(
        name="relatorio-operador",
        description="Mostra seu relatório de produção.",
    )
    @app_commands.describe(
        periodo="Período do relatório",
        data_inicial="Obrigatória apenas para período personalizado (dd/mm/aaaa)",
        data_final="Obrigatória apenas para período personalizado (dd/mm/aaaa)",
    )
    @app_commands.choices(
        periodo=[
            app_commands.Choice(name="Hoje", value="today"),
            app_commands.Choice(name="Mês", value="month"),
            app_commands.Choice(name="Período personalizado", value="custom"),
        ]
    )
    async def report_operator(
        interaction: discord.Interaction,
        periodo: app_commands.Choice[str],
        data_inicial: str | None = None,
        data_final: str | None = None,
    ):
        await send_operator_report(
            interaction,
            period=periodo.value,
            start_date_value=data_inicial,
            end_date_value=data_final,
        )
