import discord

WELCOME_ID = "Boas-vindas"
REPORTS_ID = "Análises"


WELCOME_MESSAGE = f"""{WELCOME_ID}
# 👋 Bem-vindo(a) ao LogoAli!

Para começar a utilizar o sistema, você precisa fazer seu cadastro.
Digite o comando:
### `/cadastrar`

Escolha se você é Despachante ou Operador. Após o cadastro, você receberá automaticamente o cargo correspondente e poderá utilizar o restante do servidor.

Caso tenha qualquer dúvida, estes canais podem ajudar:

📚  #como-usar

Tutoriais completos mostrando como utilizar cada parte do servidor.

❓  #faq-ajuda

Faça perguntas ou veja se sua dúvida já foi respondida por outra pessoa.

💡  #sugestoes-e-problemas

Relate bugs encontrados, dificuldades ou envie sugestões de melhorias.


Bom trabalho! 🚀
"""


REPORTS_MESSAGE = f"""{REPORTS_ID}
# 📊 Relatórios

É possível consultar a quantidade de pedidos finalizados e o valor deles.
Os relatórios podem mostrar:
• Hoje
• Mês atual
• Período personalizado
Apenas você poderá visualizar esse relatório.

## 👨‍💼 Operadores

### `/relatorio-operador`

---
## 🏢 Despachantes

### `/relatorio-despachante`

"""


async def ensure_pinned_message(
    channel: discord.TextChannel,
    identifier: str,
    content: str,
):

    try:

        pinned_messages = await channel.pins()

        for message in pinned_messages:

            if message.author == channel.guild.me and message.content.startswith(
                identifier
            ):

                if message.content != content:

                    await message.edit(
                        content=content,
                    )

                return

        message = await channel.send(
            content,
        )

        await message.pin(
            reason="Configuração automática do LogoAli.",
        )

    except Exception as e:

        print(f"Erro ao configurar #{channel.name}: {e}")


async def setup_server(
    bot: discord.Client,
):

    for guild in bot.guilds:

        welcome_channel = discord.utils.get(
            guild.text_channels,
            name="bem-vindo",
        )

        if welcome_channel is not None:

            await ensure_pinned_message(
                channel=welcome_channel,
                identifier=WELCOME_ID,
                content=WELCOME_MESSAGE,
            )

        reports_channel = discord.utils.get(
            guild.text_channels,
            name="analises",
        )

        if reports_channel is not None:

            await ensure_pinned_message(
                channel=reports_channel,
                identifier=REPORTS_ID,
                content=REPORTS_MESSAGE,
            )
