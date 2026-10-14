from io import BytesIO
from zipfile import BadZipFile

import discord
from discord import app_commands
from discord.ext import commands
from openpyxl.utils.exceptions import InvalidFileException
from sqlalchemy.exc import SQLAlchemyError

from config import USER_ROLES
from database.reports import get_order_counts_by_day
from utils.excel import create_operator_analysis_workbook, summarize_orders_by_operator


def setup_analyze_excel(bot: commands.Bot):
    @bot.tree.command(
        name="analisar-planilha",
        description="Gera uma planilha comparativa por operador, dia e banco Discord.",
    )
    @app_commands.describe(
        arquivo="Arquivo .xlsx para analisar.",
    )
    async def analyze_excel(
        interaction: discord.Interaction,
        arquivo: discord.Attachment,
    ):
        admin_role = (
            discord.utils.get(
                interaction.guild.roles,
                name=USER_ROLES["admin"],
            )
            if interaction.guild is not None
            else None
        )

        if (
            admin_role is None
            or not isinstance(interaction.user, discord.Member)
            or admin_role not in interaction.user.roles
        ):
            await interaction.response.send_message(
                "Apenas administradores podem usar este comando.",
                ephemeral=True,
            )
            return

        if not arquivo.filename.lower().endswith(".xlsx"):
            await interaction.response.send_message(
                "Envie um arquivo Excel no formato .xlsx.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            daily_counts, totals = summarize_orders_by_operator(await arquivo.read())
        except (BadZipFile, InvalidFileException, OSError, ValueError) as error:
            print(
                f"[ERRO][PLANILHA] Arquivo inválido | "
                f"nome='{arquivo.filename}' | erro={repr(error)}"
            )
            await interaction.followup.send(
                "Não foi possível analisar o arquivo. Verifique se é um .xlsx válido "
                "e segue o formato esperado.",
                ephemeral=True,
            )
            return

        if not daily_counts:
            await interaction.followup.send(
                "Não encontrei pedidos válidos nessa planilha.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        first_day = min(daily_counts)
        last_day = max(daily_counts)
        try:
            discord_counts = get_order_counts_by_day(
                guild_id=str(guild.id),
                start_date=first_day,
                end_date=last_day,
            )
        except SQLAlchemyError as error:
            print(
                f"[ERRO][PLANILHA] Não foi possível consultar pedidos do Discord | "
                f"guild={guild.id} | erro={repr(error)}"
            )
            await interaction.followup.send(
                "Não foi possível consultar os pedidos registrados no Discord. "
                "Tente novamente mais tarde.",
                ephemeral=True,
            )
            return

        workbook_content = create_operator_analysis_workbook(
            daily_counts,
            totals,
            discord_counts,
        )
        await interaction.followup.send(
            "📊 Análise pronta: o arquivo contém os totais por dia, a comparação "
            "com os pedidos registrados no Discord e os detalhes por operador.",
            file=discord.File(
                BytesIO(workbook_content),
                filename=f"analise-pedidos-{first_day:%Y%m%d}-{last_day:%Y%m%d}.xlsx",
            ),
            ephemeral=True,
        )
