from datetime import datetime

import discord
from discord import app_commands

from database.reports import (
    get_dispatcher_summary,
    get_today_period,
    get_month_period,
    get_custom_period,
)

from config import USER_ROLES


def setup_report_dispatcher(bot: discord.Client):

    @bot.tree.command(
        name="relatorio-despachante",
        description="Mostra o relatório financeiro.",
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
    async def report_dispatcher(
        interaction: discord.Interaction,
        periodo: app_commands.Choice[str],
        data_inicial: str | None = None,
        data_final: str | None = None,
    ):

        dispatcher_role = discord.utils.get(
            interaction.guild.roles,
            name=USER_ROLES["dispatcher"],
        )

        if dispatcher_role not in interaction.user.roles:
            await interaction.response.send_message(
                "Apenas despachantes podem utilizar este comando.",
                ephemeral=True,
            )
            return

        try:

            if periodo.value == "today":

                start, end = get_today_period()

            elif periodo.value == "month":

                start, end = get_month_period()

            else:

                if data_inicial is None or data_final is None:
                    raise ValueError("Informe a data inicial e a data final.")

                start_date = datetime.strptime(
                    data_inicial,
                    "%d/%m/%Y",
                )

                end_date = datetime.strptime(
                    data_final,
                    "%d/%m/%Y",
                )

                start, end = get_custom_period(
                    start_date,
                    end_date,
                )

            summary = get_dispatcher_summary(
                guild_id=str(interaction.guild.id),
                start_date=start,
                end_date=end,
            )

        except ValueError as e:

            await interaction.response.send_message(
                str(e),
                ephemeral=True,
            )

            return

        embed = discord.Embed(
            title="📊 Relatório do despachante",
            color=discord.Color.green(),
        )

        embed.add_field(
            name="PF",
            value=(
                f"Taxas: {summary['pf_amount']}\n"
                f"Valor: R$ {summary['pf_value']:.2f}"
            ),
            inline=False,
        )

        embed.add_field(
            name="PJ",
            value=(
                f"Cadastros/Reativações/Inclusões: {summary['pj_amount_cad_or_reval']}\n"
                f"Alterações/Remoções: {summary['pj_amount_alt_or_rem']}\n"
                f"Refund: R$ {summary['pj_refund_value']:.2f}"
            ),
            inline=False,
        )

        embed.add_field(
            name="Cursos",
            value=(
                f"Quantidade: {summary['course_amount']}\n"
                f"Valor: R$ {summary['course_value']:.2f}"
            ),
            inline=False,
        )

        embed.add_field(
            name="Total (PF + Cursos)",
            value=f"R$ {summary['pf_value'] + summary['course_value']:.2f}",
            inline=True,
        )

        embed.add_field(
            name="Total (PJ)",
            value=f"R$ {summary['pj_refund_value']:.2f}",
            inline=True,
        )

        embed.add_field(
            name="Resultado líquido (PF + Cursos - PJ)",
            value=f"R$ {summary['net_value']:.2f}",
            inline=False,
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )
