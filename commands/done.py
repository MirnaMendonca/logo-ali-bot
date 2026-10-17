import discord
from sqlalchemy.exc import IntegrityError

from database.order_service import create_order
from database.order_service import calculate_dispatcher_value
from database.order_service import get_existing_order

from google.sheets import append_dispatcher_order
from google.sheets import append_free_pf_order
from google.sheets import append_order
from utils.order_claim import find_claimed_operator_id
from utils.tags import set_status_tag
from views.return_order import ReturnOrderView


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
    descricao_servicos: str,
    operador: discord.Member | None,
    observacoes: str | None,
    embed_title: str,
    amount_fields: list[tuple[str, int]],
    create_order_kwargs: dict,
    attachments: list[discord.Attachment] | None = None,
    require_claimant: bool = False,
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

    guild = interaction.guild
    if guild is None:
        await interaction.response.send_message(
            "Não foi possível identificar o servidor.",
            ephemeral=True,
        )
        return

    operator_role = discord.utils.get(guild.roles, name="Operador")
    if operator_role is None or operator_role not in interaction.user.roles:
        await interaction.response.send_message(
            "Apenas operadores podem finalizar pedidos.",
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

    dispatcher = interaction.channel.owner

    if dispatcher is None:
        await interaction.response.send_message(
            "Não foi possível identificar o despachante deste pedido.",
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

    try:
        claimed_operator_id = await find_claimed_operator_id(interaction.channel)
    except (discord.Forbidden, discord.HTTPException) as error:
        print(
            "[ERRO][PEDIDO] Não foi possível verificar quem assumiu o pedido: "
            f"{error!r}"
        )
        await interaction.followup.send(
            "Não foi possível verificar quem assumiu este pedido. "
            "Confira as permissões do bot no tópico e tente novamente.",
            ephemeral=True,
        )
        return
    if require_claimant and claimed_operator_id is None:
        await interaction.followup.send(
            "Não foi possível confirmar quem assumiu este pedido. "
            "Peça para o operador assumi-lo novamente.",
            ephemeral=True,
        )
        return

    if claimed_operator_id is not None:
        if require_claimant and claimed_operator_id != interaction.user.id:
            await interaction.followup.send(
                "Somente o operador que assumiu este pedido pode finalizá-lo.",
                ephemeral=True,
            )
            return

        operador = guild.get_member(claimed_operator_id)
        if operador is None:
            try:
                operador = await guild.fetch_member(claimed_operator_id)
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException,
            ) as error:
                print(
                    "[ERRO][PEDIDO] Não foi possível localizar o operador "
                    f"que assumiu o pedido: {error!r}"
                )
                await interaction.followup.send(
                    "Não foi possível localizar o operador que assumiu este pedido. "
                    "Tente novamente ou contate um administrador.",
                    ephemeral=True,
                )
                return
    elif operador is None:
        operador = interaction.user

    if operator_role not in operador.roles:
        await interaction.followup.send(
            "O operador que assumiu o pedido não possui mais o cargo de operador.",
            ephemeral=True,
        )
        return

    files = []
    try:
        for attachment in attachments or []:
            files.append(await attachment.to_file())
    except Exception as error:
        print(f"[ERRO][ANEXOS] Não foi possível preparar os arquivos: {error!r}")
        await interaction.followup.send(
            "Não foi possível preparar os arquivos anexados. "
            "O pedido não foi finalizado; tente enviar os arquivos novamente.",
            ephemeral=True,
        )
        return

    is_free = category == "pf" and has_tag(
        interaction.channel,
        "Gratuito",
    )

    order = None

    try:
        if not is_free:
            order = get_existing_order(
                thread_id=str(interaction.channel.id),
            )

            dispatcher_value = (
                order.dispatcher_value
                if order is not None
                else calculate_dispatcher_value(
                    category=category,
                    guild_id=str(guild.id),
                    **create_order_kwargs,
                )
            )

            if dispatcher_value == 0:
                error_message = (
                    "Não é possível finalizar um pedido PJ sem taxa"
                    if category == "pj"
                    else "Não é possível finalizar um pedido sem taxa "
                    "sem a tag :free: Gratuito. Adicione a tag ao pedido "
                    "para finalizá-lo como gratuito. Consulte a documentação "
                    "de edição de tags no canal #como-usar."
                )
                await interaction.followup.send(
                    error_message,
                    ephemeral=True,
                )
                return

            if order is None:
                try:
                    order = create_order(
                        thread_id=str(interaction.channel.id),
                        guild_id=str(guild.id),
                        operator_discord_id=str(operador.id),
                        opening_name=dispatcher.display_name,
                        order_category=category,
                        client=cliente,
                        document=documento,
                        order=descricao_servicos,
                        observations=observacoes,
                        **create_order_kwargs,
                    )
                except IntegrityError:
                    order = get_existing_order(
                        thread_id=str(interaction.channel.id),
                    )

                    if order is None:
                        raise

            append_order(
                order,
                category,
            )

            append_dispatcher_order(
                order,
                category,
            )
        else:
            order = get_existing_order(
                thread_id=str(interaction.channel.id),
            )
            if order is None:
                try:
                    order = create_order(
                        thread_id=str(interaction.channel.id),
                        guild_id=str(guild.id),
                        operator_discord_id=str(operador.id),
                        opening_name=dispatcher.display_name,
                        order_category=category,
                        client=cliente,
                        document=documento,
                        order=descricao_servicos,
                        observations=observacoes,
                        calculate_values=False,
                    )
                except IntegrityError:
                    order = get_existing_order(
                        thread_id=str(interaction.channel.id),
                    )
                    if order is None:
                        raise

            append_free_pf_order(
                order,
                pf_amount=create_order_kwargs.get("pf_amount", 0),
                course_amount=create_order_kwargs.get("course_amount", 0),
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
        name="Descrição dos serviços",
        value=descricao_servicos,
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
        files=files,
        **(
            {
                "view": ReturnOrderView(
                    return_name=order.return_name if order is not None else None,
                    persist_return=not is_free,
                )
            }
            if is_free or order is not None
            else {}
        ),
    )
