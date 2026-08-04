import discord
from discord import app_commands

from database.database import SessionLocal
from database.order_service import delete_order

from google.sheets import delete_order_from_sheet

from config import USER_ROLES
from utils.tags import set_status_tag


class DeleteOrderConfirmationModal(discord.ui.Modal):

    confirmation = discord.ui.TextInput(
        label="Digite CONFIRMO para deletar o pedido.",
        placeholder="⚠️ CUIDADO. O pedido será DELETADO.",
        required=True,
        max_length=20,
    )

    def __init__(
        self,
        category: str,
    ):

        super().__init__(
            title="⚠️ Confirmar exclusão do pedido",
        )

        self.category = category

    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):

        if self.confirmation.value.strip().upper() != "CONFIRMO":

            await interaction.response.send_message(
                "Exclusão cancelada. Você deve digitar **CONFIRMO** exatamente como solicitado.",
                ephemeral=True,
            )

            return

        session = SessionLocal()

        try:

            order = delete_order(
                session=session,
                thread_id=str(interaction.channel.id),
            )

            delete_order_from_sheet(
                order=order,
                category=self.category,
            )

            session.commit()

        except ValueError as e:

            session.rollback()

            await interaction.response.send_message(
                str(e),
                ephemeral=True,
            )

            return

        except Exception as e:

            session.rollback()
            print(e)

            await interaction.response.send_message(
                "Ocorreu um erro ao deletar o pedido.",
                ephemeral=True,
            )

            return

        finally:

            session.close()

        await set_status_tag(
            interaction.channel,
            "Cancelado",
        )

        embed = discord.Embed(
            title="🗑️ Pedido removido",
            description=(
                "O pedido foi removido do banco de dados e da planilha.\n"
                "A thread foi marcada como **Cancelado**."
            ),
            color=discord.Color.red(),
        )

        await interaction.response.send_message(
            embed=embed,
        )


def setup_delete_order(bot: discord.Client):

    @bot.tree.command(
        name="deletar-pedido",
        description="Remove um pedido do sistema.",
    )
    async def delete_order_command(
        interaction: discord.Interaction,
    ):

        if not isinstance(
            interaction.channel,
            discord.Thread,
        ):
            await interaction.response.send_message(
                "Este comando só pode ser usado dentro de um pedido.",
                ephemeral=True,
            )
            return

        admin_role = discord.utils.get(
            interaction.guild.roles,
            name=USER_ROLES["admin"],
        )

        if admin_role is None or admin_role not in interaction.user.roles:

            await interaction.response.send_message(
                "Apenas administradores podem usar este comando. Contate um administrador para poder deletar este pedido. Você pode editar esse pedido ao invés de deletá-lo com o comando /editar-pedido.",
                ephemeral=True,
            )

            return

        forum = interaction.channel.parent

        if forum is None:

            await interaction.response.send_message(
                "Não foi possível identificar o fórum.",
                ephemeral=True,
            )

            return

        if "pf" in forum.name.lower():

            category = "pf"

        elif "pj" in forum.name.lower():

            category = "pj"

        else:

            await interaction.response.send_message(
                "Este comando só pode ser usado em pedidos PF ou PJ.",
                ephemeral=True,
            )

            return

        await interaction.response.send_modal(
            DeleteOrderConfirmationModal(
                category=category,
            )
        )
