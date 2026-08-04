import discord


async def set_status_tag(
    thread: discord.Thread,
    status: str,
):

    forum = thread.parent

    if not isinstance(
        forum,
        discord.ForumChannel,
    ):
        return

    status_names = {
        "Aguardando",
        "Em andamento",
        "Com pendência",
        "Finalizado",
        "Cancelado",
    }

    tags = [tag for tag in thread.applied_tags if tag.name not in status_names]

    new_status = discord.utils.get(
        forum.available_tags,
        name=status,
    )

    if new_status is None:
        raise ValueError(f"A tag '{status}' não existe neste fórum.")

    tags.append(new_status)

    await thread.edit(
        applied_tags=tags,
    )
