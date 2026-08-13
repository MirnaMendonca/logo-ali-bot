import discord
from discord.ext import commands
from dotenv import load_dotenv

from server_setup import setup_server

from config import (
    TOKEN,
    GUILDS,
)

from utils.tags import set_status_tag
from views.claim_order import ClaimOrderView

from commands.register import setup_register
from commands.done_pf import setup_done_pf
from commands.done_pj import setup_done_pj
from commands.report_operator import setup_report_operator
from commands.report_dispatcher import setup_report_dispatcher
from commands.report_general import setup_report_general
from commands.delete_order import setup_delete_order
from commands.edit_order import setup_edit_order
from commands.daily_report import setup_daily_report

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
setup_daily_report(bot)


@bot.event
async def on_thread_create(thread: discord.Thread):

    if not (
        thread.parent
        and isinstance(
            thread.parent,
            discord.ForumChannel,
        )
        and ("pf" in thread.parent.name.lower() or "pj" in thread.parent.name.lower())
    ):
        return

    print(
        f"[THREAD] Nova thread detectada | "
        f"id={thread.id} | "
        f"nome='{thread.name}' | "
        f"forum='{thread.parent.name}'"
    )

    try:

        print(f"[THREAD] Tentando adicionar tag 'Aguardando' | " f"thread={thread.id}")

        await set_status_tag(
            thread,
            "Aguardando",
        )

        print(
            f"[THREAD] Tag 'Aguardando' adicionada com sucesso | " f"thread={thread.id}"
        )

    except Exception as e:

        print(
            f"[ERRO][TAG] Não foi possível adicionar a tag "
            f"'Aguardando' | "
            f"thread={thread.id} | "
            f"nome='{thread.name}' | "
            f"erro={repr(e)}"
        )

    try:

        print(f"[THREAD] Tentando enviar mensagem e botão | " f"thread={thread.id}")

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
            f"[THREAD] Mensagem e botão enviados com sucesso | " f"thread={thread.id}"
        )

    except Exception as e:

        print(
            f"[ERRO][BOTÃO] Não foi possível enviar a mensagem "
            f"com o botão | "
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
