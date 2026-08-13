import discord

STATUS_NAMES = {
    "aguardando",
    "em andamento",
    "com pendência",
    "finalizado",
    "cancelado",
}


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

    new_status = discord.utils.get(
        forum.available_tags,
        name=status,
    )

    if new_status is None:
        raise ValueError(f"A tag '{status}' não existe neste fórum.")

    tags = [
        tag
        for tag in thread.applied_tags
        if tag.name.strip().lower() not in STATUS_NAMES
    ]

    tags.append(new_status)

    await thread.edit(
        applied_tags=tags,
    )
