import discord

from config import USER_ROLES
from database.order_service import record_order_return
from google.sheets import update_dispatcher_return_name


class ReturnOrderView(discord.ui.View):
    def __init__(
        self,
        *,
        return_name: str | None = None,
        persist_return: bool = True,
    ):
        super().__init__(timeout=None)
        self.persist_return = persist_return
        if return_name is not None:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.label = f"Devolução registrada: {return_name}"
                    item.disabled = True
        if not persist_return:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    item.custom_id = "record_free_order_return"

    @discord.ui.button(
        label="Registrar devolução",
        emoji="↩️",
        style=discord.ButtonStyle.danger,
        custom_id="record_order_return",
    )
    async def record_return(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if not isinstance(interaction.channel, discord.Thread):
            await interaction.response.send_message(
                "Este botão só pode ser usado dentro de um pedido.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "Não foi possível identificar o servidor.",
                ephemeral=True,
            )
            return

        dispatcher_role = discord.utils.get(
            guild.roles,
            name=USER_ROLES["dispatcher"],
        )

        if dispatcher_role is None:
            await interaction.response.send_message(
                f"O cargo **{USER_ROLES['dispatcher']}** não foi encontrado neste servidor.",
                ephemeral=True,
            )
            return

        if (
            not isinstance(interaction.user, discord.Member)
            or dispatcher_role not in interaction.user.roles
        ):
            await interaction.response.send_message(
                "Apenas despachantes podem registrar a devolução.",
                ephemeral=True,
            )
            return

        return_name = interaction.user.display_name

        if not self.persist_return:
            await interaction.response.edit_message(
                view=ReturnOrderView(
                    return_name=return_name,
                    persist_return=False,
                ),
            )
            return

        try:
            order = record_order_return(
                thread_id=str(interaction.channel.id),
                return_name=return_name,
            )
        except ValueError as error:
            await interaction.response.send_message(
                str(error),
                ephemeral=True,
            )
            return
        except Exception as error:
            print(f"[ERRO][DEVOLUÇÃO] Não foi possível salvar no banco: {error!r}")
            await interaction.response.send_message(
                "Ocorreu um erro ao registrar a devolução. Tente novamente.",
                ephemeral=True,
            )
            return

        try:
            update_dispatcher_return_name(
                order,
                return_name,
            )
        except Exception as error:
            print(f"[ERRO][DEVOLUÇÃO] Não foi possível atualizar a planilha: {error!r}")
            await interaction.response.send_message(
                "A devolução foi salva no banco, mas não foi possível atualizar "
                "a planilha. Clique novamente para tentar sincronizar.",
                ephemeral=True,
            )
            return

        await interaction.response.edit_message(
            view=ReturnOrderView(return_name=return_name),
        )
