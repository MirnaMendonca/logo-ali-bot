import discord

from database.order_service import create_order

from google.sheets import append_order
from utils.tags import set_status_tag


def has_tag(
    thread: discord.Thread,
    tag_name: str,
) -> bool:

    return any(tag.name.lower() == tag_name.lower() for tag in thread.applied_tags)


async def finish_order(
    *,
    interaction: discord.Interaction,
    category: str,
    cliente: str,
    documento: str,
    pedidos: str,
    operador: discord.Member | None,
    observacoes: str | None,
    embed_title: str,
    amount_fields: list[tuple[str, int]],
    create_order_kwargs: dict,
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

    operator_role = discord.utils.get(
        interaction.guild.roles,
        name="Operador",
    )

    if operator_role is None or operator_role not in interaction.user.roles:
        await interaction.response.send_message(
            "Apenas operadores podem finalizar pedidos.",
            ephemeral=True,
        )
        return

    if operador is None:
        operador = interaction.user

    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "Não foi possível identificar o servidor.",
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

    if category not in forum.name.lower():
        await interaction.response.send_message(
            f"Este comando só pode ser utilizado em pedidos {category.upper()}.",
            ephemeral=True,
        )
        return

    if has_tag(
        interaction.channel,
        "Finalizado",
    ):
        await interaction.response.send_message(
            "Este pedido já foi finalizado.",
            ephemeral=True,
        )
        return

    if has_tag(
        interaction.channel,
        "Cancelado",
    ):
        await interaction.response.send_message(
            "Este pedido foi cancelado e não pode ser finalizado.",
            ephemeral=True,
        )
        return

    if has_tag(
        interaction.channel,
        "Com pendência",
    ):
        await interaction.response.send_message(
            "Este pedido possui pendências e não pode ser finalizado. Contate um administrador.",
            ephemeral=True,
        )
        return

    await interaction.response.defer()

    is_free = has_tag(
        interaction.channel,
        "Gratuito",
    )

    if not is_free:

        try:

            order = create_order(
                thread_id=str(interaction.channel.id),
                guild_id=str(guild.id),
                operator_discord_id=str(operador.id),
                order_category=category,
                client=cliente,
                document=documento,
                order=pedidos,
                observations=observacoes,
                **create_order_kwargs,
            )

            append_order(
                order,
                category,
            )

        except ValueError as e:

            await interaction.followup.send(
                str(e),
                ephemeral=True,
            )
            return

        except Exception as e:

            print(e)

            await interaction.followup.send(
                "Ocorreu um erro inesperado ao finalizar o pedido.",
                ephemeral=True,
            )
            return

    await set_status_tag(
        interaction.channel,
        "Finalizado",
    )

    embed = discord.Embed(
        title=embed_title,
        color=discord.Color.green(),
    )

    embed.add_field(
        name="Cliente",
        value=cliente,
        inline=False,
    )

    embed.add_field(
        name="CPF" if category == "pf" else "CNPJ",
        value=documento,
        inline=False,
    )

    embed.add_field(
        name="Pedidos",
        value=pedidos,
        inline=False,
    )

    for field_name, value in amount_fields:

        embed.add_field(
            name=field_name,
            value=str(value),
            inline=True,
        )

    embed.add_field(
        name="Operador",
        value=operador.mention,
        inline=False,
    )

    if observacoes:

        embed.add_field(
            name="Observações",
            value=observacoes,
            inline=False,
        )

    if is_free:

        embed.add_field(
            name="Situação",
            value="🆓 Pedido gratuito",
            inline=False,
        )

    await interaction.followup.send(
        embed=embed,
    )
