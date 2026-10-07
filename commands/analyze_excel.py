from io import BytesIO
from zipfile import BadZipFile

import discord
from discord import app_commands
from discord.ext import commands
from openpyxl.utils.exceptions import InvalidFileException

from config import USER_ROLES
from utils.excel import format_operator_summary, summarize_orders_by_operator


def setup_analyze_excel(bot: commands.Bot):
    @bot.tree.command(
        name="analisar-planilha",
        description="Resume os pedidos por operador e por dia.",
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

        summary = format_operator_summary(daily_counts, totals)
        if len(summary) > 1900:
            await interaction.followup.send(
                "O resumo completo está no arquivo de texto anexado.",
                file=discord.File(
                    BytesIO(summary.encode("utf-8")),
                    filename="resumo-operadores.txt",
                ),
                ephemeral=True,
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        await interaction.followup.send(
            f"📊\n{summary}",
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions.none(),
        )
