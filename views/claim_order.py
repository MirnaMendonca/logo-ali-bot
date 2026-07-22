import discord

from config import USER_ROLES


class ClaimOrderView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

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

        operator_role = discord.utils.get(
            interaction.guild.roles,
            name=USER_ROLES["operator"],
        )

        if operator_role is None:
            await interaction.response.send_message(
                f"O cargo **{USER_ROLES['operator']}** não foi encontrado neste servidor.",
                ephemeral=True,
            )
            return

        if operator_role not in interaction.user.roles:
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

        waiting_tag = discord.utils.get(
            forum.available_tags,
            name="Aguardando",
        )

        in_progress_tag = discord.utils.get(
            forum.available_tags,
            name="Em andamento",
        )

        if waiting_tag is None:
            await interaction.response.send_message(
                "A tag 'Aguardando' não foi encontrada.",
                ephemeral=True,
            )
            return

        if in_progress_tag is None:
            await interaction.response.send_message(
                "A tag 'Em andamento' não foi encontrada.",
                ephemeral=True,
            )
            return

        if "pf" in forum.name.lower():
            finish_command = "/feito-pf"
        elif "pj" in forum.name.lower():
            finish_command = "/feito-pj"
        else:
            finish_command = "/feito"

        # Pedido livre
        if button.label == "Assumir pedido":

            await thread.edit(
                applied_tags=[in_progress_tag],
            )

            button.label = f"Assumido por {interaction.user.display_name}"

            embed = discord.Embed(
                title="🔵 Serviço em andamento",
                description=(
                    f"**Operador:** {interaction.user.mention}\n\n"
                    f"Quando finalizar o serviço, utilize o comando **{finish_command}**."
                ),
                color=discord.Color.blue(),
            )

            await interaction.response.edit_message(
                embed=embed,
                view=self,
            )

            return

        # O mesmo operador devolveu o pedido
        if button.label == f"Assumido por {interaction.user.display_name}":

            await thread.edit(
                applied_tags=[waiting_tag],
            )

            button.label = "Assumir pedido"

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
        operator_name = button.label.removeprefix("Assumido por ")

        await interaction.response.send_message(
            f"Este pedido já está sendo atendido por **{operator_name}**.",
            ephemeral=True,
        )
