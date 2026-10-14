import discord

from commands.done import has_tag
from config import USER_ROLES
from utils.order_claim import (
    CLAIMED_OPERATOR_FOOTER,
    get_claimed_operator_id,
)
from utils.tags import set_status_tag
from views.finish_order import FinishOrderDetailsModal


class ClaimOrderView(discord.ui.View):
    def __init__(self, *, claimed: bool = False):
        super().__init__(timeout=None)
        self.finish_button = discord.utils.get(
            self.children,
            custom_id="finish_order",
        )
        self.finish_button.disabled = not claimed

    @discord.ui.button(
        label="Assumir pedido",
        emoji="▶️",
        style=discord.ButtonStyle.primary,
        custom_id="claim_order",
    )
    async def claim_order(
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

        operator_role = discord.utils.get(
            guild.roles,
            name=USER_ROLES["operator"],
        )

        if operator_role is None:
            await interaction.response.send_message(
                f"O cargo **{USER_ROLES['operator']}** não foi encontrado neste servidor.",
                ephemeral=True,
            )
            return

        if not isinstance(interaction.user, discord.Member) or (
            operator_role not in interaction.user.roles
        ):
            await interaction.response.send_message(
                "Apenas operadores podem assumir pedidos.",
                ephemeral=True,
            )
            return

        thread = interaction.channel
        forum = thread.parent

        if forum is None:
            await interaction.response.send_message(
                "Não foi possível identificar a categoria do pedido.",
                ephemeral=True,
            )
            return

        claimed_operator_id = get_claimed_operator_id(interaction.message)

        if claimed_operator_id is None and button.label == "Assumir pedido":

            await set_status_tag(
                thread,
                "Em andamento",
            )

            button.label = f"Assumido por {interaction.user.display_name}"

            embed = discord.Embed(
                title="🔵 Serviço em andamento",
                description=(
                    f"**Operador:** {interaction.user.mention}\n\n"
                    "Quando finalizar o serviço, clique em **Finalizar pedido**."
                ),
                color=discord.Color.blue(),
            )
            embed.set_footer(text=f"{CLAIMED_OPERATOR_FOOTER}{interaction.user.id}")
            self.finish_button.disabled = False

            await interaction.response.edit_message(
                embed=embed,
                view=self,
            )

            return

        # O mesmo operador devolveu o pedido
        if claimed_operator_id == interaction.user.id:

            await set_status_tag(
                thread,
                "Aguardando",
            )

            button.label = "Assumir pedido"
            self.finish_button.disabled = True

            embed = discord.Embed(
                title="🟡 Serviço aguardando operador",
                description="Clique no botão abaixo para assumir este serviço.",
                color=discord.Color.gold(),
            )

            await interaction.response.edit_message(
                embed=embed,
                view=self,
            )

            return

        # Outro operador tentou assumir
        claimed_operator = (
            guild.get_member(claimed_operator_id)
            if claimed_operator_id is not None
            else None
        )
        operator_name = (
            claimed_operator.display_name
            if claimed_operator is not None
            else button.label.removeprefix("Assumido por ")
        )
        if operator_name == "Assumir pedido":
            operator_name = "outro operador"

        await interaction.response.send_message(
            f"Este pedido já está sendo atendido por **{operator_name}**.",
            ephemeral=True,
        )

    @discord.ui.button(
        label="Finalizar pedido",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="finish_order",
        disabled=True,
    )
    async def finish_order(
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

        operator_role = discord.utils.get(
            guild.roles,
            name=USER_ROLES["operator"],
        )
        if operator_role is None:
            await interaction.response.send_message(
                f"O cargo **{USER_ROLES['operator']}** não foi encontrado neste servidor.",
                ephemeral=True,
            )
            return

        if not isinstance(interaction.user, discord.Member) or (
            operator_role not in interaction.user.roles
        ):
            await interaction.response.send_message(
                "Apenas operadores podem finalizar pedidos.",
                ephemeral=True,
            )
            return

        if has_tag(interaction.channel, "Finalizado"):
            await interaction.response.send_message(
                "Este pedido já foi finalizado.",
                ephemeral=True,
            )
            return

        forum = interaction.channel.parent
        if forum is None:
            await interaction.response.send_message(
                "Não foi possível identificar a categoria do pedido.",
                ephemeral=True,
            )
            return

        claimed_operator_id = get_claimed_operator_id(interaction.message)
        if claimed_operator_id is None:
            await interaction.response.send_message(
                "Este pedido ainda não foi assumido por um operador.",
                ephemeral=True,
            )
            return

        if claimed_operator_id != interaction.user.id:
            await interaction.response.send_message(
                "Somente o operador que assumiu este pedido pode finalizá-lo.",
                ephemeral=True,
            )
            return

        if "pf" in forum.name.lower():
            category = "pf"
        elif "pj" in forum.name.lower():
            category = "pj"
        else:
            await interaction.response.send_message(
                "Não foi possível identificar se este pedido é PF ou PJ.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(
            FinishOrderDetailsModal(
                category,
                user_id=interaction.user.id,
            )
        )
