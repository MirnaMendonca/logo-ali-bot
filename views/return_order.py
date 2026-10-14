import discord

from config import USER_ROLES
from database.order_service import record_order_return
from google.sheets import update_dispatcher_return_name

RETURN_NAMES = (
    "Administração",
    "Kauan",
    "João",
    "Sophia",
    "Alana",
)


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
                    item.label = f"Devolução: {return_name}"
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

        if interaction.message is None:
            await interaction.response.send_message(
                "Não foi possível identificar a mensagem do pedido.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Selecione seu nome para registrar a devolução.",
            view=ReturnOrderSelectionView(
                original_message=interaction.message,
                thread_id=str(interaction.channel.id),
                user_id=interaction.user.id,
                persist_return=self.persist_return,
            ),
            ephemeral=True,
        )


class ReturnOrderSelectionView(discord.ui.View):
    def __init__(
        self,
        *,
        original_message: discord.Message,
        thread_id: str,
        user_id: int,
        persist_return: bool,
    ):
        super().__init__(timeout=180)
        self.original_message = original_message
        self.thread_id = thread_id
        self.user_id = user_id
        self.persist_return = persist_return

    @discord.ui.select(
        placeholder="Selecione seu nome",
        options=[discord.SelectOption(label=name, value=name) for name in RETURN_NAMES],
        min_values=1,
        max_values=1,
    )
    async def select_return_name(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select,
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Somente quem abriu esta seleção pode registrar a devolução.",
                ephemeral=True,
            )
            return

        return_name = select.values[0]
        if return_name not in RETURN_NAMES:
            await interaction.response.send_message(
                "O nome selecionado não é válido.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        dispatcher_role = (
            discord.utils.get(
                guild.roles,
                name=USER_ROLES["dispatcher"],
            )
            if guild is not None
            else None
        )
        if (
            not isinstance(interaction.user, discord.Member)
            or dispatcher_role is None
            or dispatcher_role not in interaction.user.roles
        ):
            await interaction.response.send_message(
                "Apenas despachantes podem registrar a devolução.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        if not self.persist_return:
            try:
                await self.original_message.edit(
                    view=ReturnOrderView(
                        return_name=return_name,
                        persist_return=False,
                    ),
                )
            except Exception as error:
                print(
                    f"[ERRO][DEVOLUÇÃO] Não foi possível atualizar a mensagem: "
                    f"{error!r}"
                )
                await interaction.edit_original_response(
                    content="Não foi possível atualizar a mensagem do pedido. "
                    "Tente novamente.",
                    view=None,
                )
                return

            await interaction.edit_original_response(
                content=f"Devolução registrada: **{return_name}**.",
                view=None,
            )
            return

        try:
            order = record_order_return(
                thread_id=self.thread_id,
                return_name=return_name,
            )
        except ValueError as error:
            await interaction.edit_original_response(
                content=str(error),
                view=None,
            )
            return
        except Exception as error:
            print(f"[ERRO][DEVOLUÇÃO] Não foi possível salvar no banco: {error!r}")
            await interaction.edit_original_response(
                content="Ocorreu um erro ao registrar a devolução. Tente novamente.",
                view=None,
            )
            return

        try:
            update_dispatcher_return_name(
                order,
                return_name,
            )
        except Exception as error:
            print(f"[ERRO][DEVOLUÇÃO] Não foi possível atualizar a planilha: {error!r}")
            await interaction.edit_original_response(
                content="A devolução foi salva no banco, mas não foi possível "
                "atualizar a planilha. Clique novamente e selecione o mesmo "
                "nome para tentar sincronizar.",
                view=None,
            )
            return

        try:
            await self.original_message.edit(
                view=ReturnOrderView(return_name=return_name),
            )
        except Exception as error:
            print(
                f"[ERRO][DEVOLUÇÃO] Não foi possível atualizar a mensagem: "
                f"{error!r}"
            )
            await interaction.edit_original_response(
                content=f"A devolução de **{return_name}** foi salva, mas não "
                "foi possível atualizar o botão do pedido.",
                view=None,
            )
            return

        await interaction.edit_original_response(
            content=f"Devolução registrada: **{return_name}**.",
            view=None,
        )
