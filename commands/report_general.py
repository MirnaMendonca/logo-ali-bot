import discord
from discord import app_commands

from database.reports import get_general_summary

from config import USER_ROLES


def setup_report_general(bot: discord.Client):

    @bot.tree.command(
        name="relatorio-geral",
        description="Mostra o resumo financeiro do servidor.",
    )
    async def report_general(
        interaction: discord.Interaction,
    ):

        admin_role = discord.utils.get(
            interaction.guild.roles,
            name=USER_ROLES["admin"],
        )

        if admin_role not in interaction.user.roles:

            await interaction.response.send_message(
                "Apenas administradores podem utilizar este comando.",
                ephemeral=True,
            )

            return

        try:

            summary = get_general_summary(
                guild_id=str(interaction.guild.id),
            )

        except ValueError as e:

            await interaction.response.send_message(
                str(e),
                ephemeral=True,
            )

            return

        dispatcher = summary["dispatcher"]

        embed = discord.Embed(
            title="📊 Relatório Geral",
            color=discord.Color.gold(),
        )

        embed.add_field(
            name="💰 Cobrança do despachante (Hoje)",
            value=(
                f"PF: {dispatcher['pf_amount']}\n"
                f"Cursos: {dispatcher['course_amount']}\n"
                f"Valor (PF + Cursos): {(dispatcher['pf_value'] + dispatcher['course_value']):.2f}\n"
                f"PJ Cadastro/Reativação/Inclusão: {dispatcher['pj_amount_cad_or_reval']}\n"
                f"PJ Alteração/Remoção: {dispatcher['pj_amount_alt_or_rem']}\n"
                f"Valor (PJ): {dispatcher['pj_refund_value']}\n\n"
                f"**Total a cobrar:** "
                f"R$ {dispatcher['net_value']:.2f}\n"
            ),
            inline=False,
        )

        if summary["operators"]:

            operator_lines = []

            for operator in summary["operators"]:

                operator_lines.append(
                    (
                        f"**{operator['name']}**\n"
                        f"Pedidos: {operator['orders']}\n"
                        f"Receber: R$ {operator['value']:.2f}"
                    )
                )

            embed.add_field(
                name="👷 Operadores (Semana de pagamento)",
                value="\n\n".join(operator_lines),
                inline=False,
            )

        else:

            embed.add_field(
                name="👷 Operadores",
                value="Nenhum pedido na semana de pagamento.",
                inline=False,
            )

        embed.add_field(
            name="💵 Total a pagar aos operadores",
            value=f"R$ {summary['operators_total']:.2f}",
            inline=False,
        )

        embed.set_footer(
            text=(
                "Despachante: valores de hoje • "
                f"Operadores: desde {summary['payment_week_start'].strftime('%d/%m/%Y')}"
            )
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )
