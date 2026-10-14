import re

import discord

CLAIMED_OPERATOR_FOOTER = "claimed-operator:"
CLAIMED_OPERATOR_PATTERN = re.compile(r"\*\*Operador:\*\*\s*<@!?(\d+)>")


def get_claimed_operator_id(message: discord.Message | None) -> int | None:
    if message is None or not message.author.bot or not message.embeds:
        return None

    embed = message.embeds[0]
    footer = embed.footer.text or ""
    if footer.startswith(CLAIMED_OPERATOR_FOOTER):
        try:
            return int(footer.removeprefix(CLAIMED_OPERATOR_FOOTER))
        except ValueError:
            return None

    if embed.title != "🔵 Serviço em andamento":
        return None

    match = CLAIMED_OPERATOR_PATTERN.search(embed.description or "")
    return int(match.group(1)) if match else None


async def find_claimed_operator_id(thread: discord.Thread) -> int | None:
    async for message in thread.history(limit=100):
        operator_id = get_claimed_operator_id(message)
        if operator_id is not None:
            return operator_id

    return None
