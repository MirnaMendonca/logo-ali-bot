import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from server_setup import setup_server

from config import (
    TOKEN,
    GUILDS,
)

from utils.tags import set_status_tag
from utils.tags import STATUS_NAMES
from views.claim_order import ClaimOrderView
from views.return_order import ReturnOrderView

from commands.register import setup_register
from commands.done_pf import setup_done_pf
from commands.done_pj import setup_done_pj
from commands.report_operator import setup_report_operator
from commands.report_dispatcher import setup_report_dispatcher
from commands.report_general import setup_report_general
from commands.delete_order import setup_delete_order
from commands.edit_order import setup_edit_order
from commands.daily_report import setup_daily_report
from commands.analyze_excel import setup_analyze_excel

from tasks.daily_reports import send_daily_reports
from database.database import ensure_schema

load_dotenv()
ensure_schema()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
)

bot.add_view(ClaimOrderView())
bot.add_view(ReturnOrderView())
bot.add_view(ReturnOrderView(persist_return=False))
order_reconciliation_lock = asyncio.Lock()

setup_register(bot)
setup_done_pf(bot)
setup_done_pj(bot)
setup_report_operator(bot)
setup_report_dispatcher(bot)
setup_report_general(bot)
setup_delete_order(bot)
setup_edit_order(bot)
setup_daily_report(bot)
setup_analyze_excel(bot)


def is_order_forum(channel):
    return isinstance(channel, discord.ForumChannel) and (
        "pf" in channel.name.lower() or "pj" in channel.name.lower()
    )


async def wait_for_initial_thread_message(thread: discord.Thread):
    for attempt in range(6):
        try:
            await thread.fetch_message(thread.id)
            return True
        except discord.NotFound:
            if attempt < 5:
                await asyncio.sleep(2)
        except discord.Forbidden:
            return False

    return False


async def ensure_order_thread_setup(thread: discord.Thread):
    if not is_order_forum(thread.parent):
        return

    async with order_reconciliation_lock:
        if not await wait_for_initial_thread_message(thread):
            print(
                f"[BOTÃO] Mensagem inicial ainda não disponível | "
                f"thread={thread.id}"
            )
            return

        if not any(
            tag.name.strip().lower() in STATUS_NAMES for tag in thread.applied_tags
        ):
            await set_status_tag(thread, "Aguardando")

        embed = discord.Embed(
            title="🟡 Pedido aguardando",
            description="Clique abaixo para assumir o pedido.",
            color=discord.Color.gold(),
        )

        await thread.send(
            embed=embed,
            view=ClaimOrderView(),
        )

        print(
            f"[BOTÃO] Botão de assumir adicionado | "
            f"thread={thread.id} | nome='{thread.name}'"
        )


@bot.event
async def on_thread_create(thread: discord.Thread):
    if not is_order_forum(thread.parent):
        return

    print(
        f"[THREAD] Nova thread detectada | "
        f"id={thread.id} | nome='{thread.name}' | forum='{thread.parent.name}'"
    )

    try:
        await ensure_order_thread_setup(thread)
    except Exception as e:
        print(
            f"[ERRO][THREAD] Não foi possível configurar "
            f"thread={thread.id} | "
            f"nome='{thread.name}' | "
            f"erro={repr(e)}"
        )


@bot.event
async def on_ready():

    print(f"[BOT] Conectado como {bot.user} | " f"id={bot.user.id}")

    for guild_id in GUILDS.keys():

        print(f"[BOT] Sincronizando comandos | " f"guild={guild_id}")

        guild = discord.Object(
            id=int(guild_id),
        )

        bot.tree.copy_global_to(
            guild=guild,
        )

        await bot.tree.sync(
            guild=guild,
        )

        print(f"[BOT] Comandos sincronizados | " f"guild={guild_id}")

    if not hasattr(
        bot,
        "daily_task",
    ):

        print("[BOT] Iniciando tarefa de relatórios diários.")

        bot.daily_task = bot.loop.create_task(
            send_daily_reports(bot),
        )

    print(f"✅ Logado como {bot.user}")

    await setup_server(bot)


bot.run(TOKEN)
