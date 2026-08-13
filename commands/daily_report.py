from discord import app_commands
import discord

from tasks.daily_reports import send_daily_report
from config import USER_ROLES


def setup_daily_report(bot: discord.Client):

    @bot.tree.command(
        name="fechamento-diario",
        description="Envia manualmente o fechamento diário.",
    )
    async def daily_report(
        interaction: discord.Interaction,
    ):

        admin_role = discord.utils.get(
            interaction.guild.roles,
            name=USER_ROLES["admin"],
        )

        if admin_role is None or admin_role not in interaction.user.roles:

            await interaction.response.send_message(
                "Apenas administradores podem usar este comando.",
                ephemeral=True,
            )

            return

        await interaction.response.defer(
            ephemeral=True,
        )

        try:

            await send_daily_report(
                guild=interaction.guild,
            )

            await interaction.followup.send(
                "✅ Fechamento diário enviado com sucesso.",
                ephemeral=True,
            )

        except Exception as e:

            print(e)

            await interaction.followup.send(
                f"❌ Erro ao enviar o fechamento: {e}",
                ephemeral=True,
            )
