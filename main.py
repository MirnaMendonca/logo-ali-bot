import discord
from discord.ext import commands
from dotenv import load_dotenv

from server_setup import setup_server

from config import (
    TOKEN,
    GUILDS,
)

from views.claim_order import ClaimOrderView

from commands.register import setup_register
from commands.done_pf import setup_done_pf
from commands.done_pj import setup_done_pj
from commands.report_operator import setup_report_operator
from commands.report_dispatcher import setup_report_dispatcher
from commands.report_general import setup_report_general
from commands.delete_order import setup_delete_order
from commands.edit_order import setup_edit_order

from tasks.daily_reports import send_daily_reports

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)

bot.add_view(ClaimOrderView())

setup_register(bot)
setup_done_pf(bot)
setup_done_pj(bot)
setup_report_operator(bot)
setup_report_dispatcher(bot)
setup_report_general(bot)
setup_delete_order(bot)
setup_edit_order(bot)


@bot.event
async def on_thread_create(thread: discord.Thread):

    try:

        if (
            thread.parent
            and isinstance(
                thread.parent,
                discord.ForumChannel,
            )
            and (
                "pf" in thread.parent.name.lower() or "pj" in thread.parent.name.lower()
            )
        ):

            waiting_tag = discord.utils.get(
                thread.parent.available_tags,
                name="Aguardando",
            )

            if waiting_tag is not None:

                await thread.edit(
                    applied_tags=[waiting_tag],
                )

            embed = discord.Embed(
                title="🟡 Pedido aguardando",
                description=(
                    f"**Despachante:** {thread.owner.mention}\n\n"
                    "Clique abaixo para assumir este pedido."
                ),
                color=discord.Color.gold(),
            )

            await thread.send(
                embed=embed,
                view=ClaimOrderView(),
            )

    except Exception as e:

        print(e)


@bot.event
async def on_ready():

    for guild_id in GUILDS.keys():

        guild = discord.Object(
            id=int(guild_id),
        )

        bot.tree.copy_global_to(
            guild=guild,
        )

        await bot.tree.sync(
            guild=guild,
        )

    if not hasattr(
        bot,
        "daily_task",
    ):

        bot.daily_task = bot.loop.create_task(
            send_daily_reports(bot),
        )

    print(f"✅ Logado como {bot.user}")

    await setup_server(bot)


bot.run(TOKEN)
