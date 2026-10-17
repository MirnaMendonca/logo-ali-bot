import discord

from config import GUILDS
from views.panels import OperatorReportPanelView
from views.panels import RegisterPanelView

WELCOME_ID = "Boas-vindas"
REPORTS_ID = "Análises"
REGISTRATION_ID = "Cadastro"


WELCOME_MESSAGE = f"""{WELCOME_ID}
# 👋 Bem-vindo(a) ao LogoAli!

Para começar a utilizar o sistema, você precisa fazer seu cadastro.
Vá no canal #cadastre-se-aqui logo abaixo desse canal e clique no botão de cadastro.

Escolha se você é Despachante ou Operador. Após o cadastro, você receberá automaticamente o cargo correspondente e poderá utilizar o restante do servidor.

Caso tenha qualquer dúvida, estes canais podem ajudar:

📚  #como-usar

Tutoriais completos mostrando como utilizar cada parte do servidor. **É extremamente recomendável ler os tutoriais!**

❓  #faq-ajuda

Faça perguntas ou veja se sua dúvida já foi respondida por outra pessoa.

💡  #sugestoes-e-bugs

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

Use os botões abaixo para gerar seu relatório. O comando `/relatorio-operador`
continua disponível como alternativa.

## 👨‍💼 Operadores

### `/relatorio-operador`

"""


# ============================================================
# Tutoriais do fórum #como-usar
# ============================================================

GUIDE_POSTS = {
    "Guia de Cadastro e Relatórios": """
## 1. Cadastro no sistema

No canal #cadastre-se-aqui, clique em **Fazer meu cadastro** e escolha se você
é Despachante ou Operador. O bot fará seu cadastro e adicionará o cargo
correspondente automaticamente.

Cada pessoa só pode ter uma função cadastrada. Se precisar corrigir um cadastro,
contate um administrador.

## 2. Relatório do operador

No canal #analises, use um dos botões:

- **Hoje**: mostra os pedidos finalizados hoje.
- **Mês**: mostra os pedidos finalizados no mês atual.
- **Período personalizado**: informe as datas inicial e final no formato
  `dd/mm/aaaa`.

O relatório é privado: somente você consegue ver o resultado. Apenas operadores
cadastrados podem consultá-lo. Os comandos `/cadastrar` e
`/relatorio-operador` continuam disponíveis como alternativas.
""",
    "Guia do Despachante - Criando e Acompanhando Pedidos": """
## 1. Como criar um pedido

Entre na categoria correspondente ao serviço. Pedidos PF devem ser postados no canal descomplica-pf, e pedidos PJ no canal descomplica-pj

Clique em Novo Post e coloque o tipo do pedido no título.
Na mensagem escreva todas as informações necessárias para o operador realizar o serviço.
Use o ícone de clipe de papel para anexar os documentos necessários.
E então clique em Publicar.

## 2. Tags no pedido

Assim que o pedido for criado ele ficará com a tag :yellow_circle: Aguardando

Quando algum operador assumir o serviço, aparecerá :blue_circle: Em andamento

Quando terminar ela receberá a tag :green_circle: Finalizado

Caso exista algum problema, adicione a tag :red_circle: Com pendência e o pedido não poderá ser finalizado enquanto estiver com essa tag. Depois que o problema for solucionado, apenas retire a tag.

Se for necessário cancelar o pedido, adicione a tag :white_circle: Cancelado e o pedido não poderá ser finalizado enquanto estiver com essa tag. Depois que o problema for solucionado, apenas retire a tag.

## 3. Pedido gratuito

Se um serviço não deve ser cobrado, por favor adicione a tag  :free: Gratuito. Assim esse pedido não será contabilizado nos relatórios financeiros.
### !IMPORTANTE! Se NÃO marcar com a tag :free: Gratuito, o sistema irá COBRAR PELO PEDIDO.


## 4. Acompanhar um pedido

Basta abrir o post. É possível pesquisar pelo seu nome no mesmo campo onde as postagens são criadas ou filtrar por tags.

## 5. Boas práticas

:white_check_mark: Um post para cada pedido.

:white_check_mark: Sempre envie todos os documentos necessários no mesmo post.

:white_check_mark: Caso esqueça alguma informação, responda no próprio post.
""",
    "Guia do Operador - Assumindo e Devolvendo Pedidos": """
## 1. Assumindo um serviço

Abra um pedido que esteja com a tag :yellow_circle: Aguardando.
Clique no botão :arrow_forward: **Assumir pedido**. O sistema irá marcar como
:blue_circle: Em andamento e mostrará quem assumiu. Enquanto o pedido estiver
com você, outro operador não poderá assumi-lo.

## 2. Devolver um serviço

Caso tenha assumido por engano ou não consiga realizar o serviço, clique
novamente no botão que agora mostra seu nome. Somente a pessoa que assumiu
consegue devolver o pedido dessa forma. Ele voltará para :yellow_circle:
Aguardando e outra pessoa poderá assumi-lo.

## 3. Regras importantes

:white_check_mark: Sempre assuma o pedido antes de começar, para que não haja confusões sobre qual operador está fazendo o pedido.

:white_check_mark: Somente quem assumiu o pedido pode usar o botão **Finalizar pedido**. Quem assumiu também será registrado como o operador do serviço.

:white_check_mark: Se não conseguir completar um pedido, devolva-o para que outra pessoa possa assumir.
""",
    "Guia do Operador - Finalizando Pedidos": """
## 1. Finalizando um serviço

Depois de assumir o pedido e concluir o serviço, clique em **Finalizar pedido**.
O formulário identifica automaticamente se o pedido é PF ou PJ.

### Em pedidos PF

Preencha:

- cliente: Nome do cliente
- CPF: CPF do cliente
- descricao_servicos: Descreva os serviços realizados, por exemplo: "TAC + Cadastro" ou "Mercosul com arrendamento"
- quantidade: Quantidade de taxas cobradas. Por exemplo: um cadastro com 3 placas são 3 taxas, inclusão de 2 placas são 2 taxas.
- exclusoes_pj: Quantidade de exclusões no CNPJ antes da inclusão no CPF.

### Em pedidos PJ

Preencha:

- cliente: Nome do cliente
- CNPJ: CNPJ do cliente
- descricao_servicos: Descreva os serviços realizados, por exemplo: "Alteração + Exclusão" ou "Cadastro + 3 Inclusões"
- cadastros_inclusoes: Quantidade de serviços que são Cadastros, Inclusões ou Reativações.
- alteracoes_exclusoes: Quantidade de serviços que são Alterações ou Exclusões.

No segundo formulário, você pode preencher observações e anexar até 10 arquivos.
Os arquivos serão publicados junto ao resumo no próprio pedido, onde o
despachante poderá baixá-los.

Os comandos `/feito-pf` e `/feito-pj` continuam disponíveis. Quando o pedido
foi assumido, o responsável registrado será quem o assumiu, mesmo que outro
operador use o comando.

## 2. Pedido gratuito

Se o pedido PF possuir a tag :free: Gratuito finalize-o normalmente. Ele não será contabilizado financeiramente.
Pedidos PF sem taxa só podem ser finalizados com essa tag. Consulte o tutorial **Adicionando e Removendo Tags** no canal #como-usar para saber como adicioná-la.
Pedidos PJ não podem ser gratuitos e não podem ser finalizados sem taxa.

## Regras importantes

:white_check_mark: Não finalize pedidos incompletos. Envie a documentação necessária ao finalizar o pedido.

:white_check_mark: Confira todas as informações antes de enviar.
""",
    "Editando e Deletando Pedidos": """
## Editando pedidos

Use o comando:

```/editar-pedido```

para corrigir informações de um pedido já finalizado, como:

- Nome do cliente
- CPF/CNPJ
- Descrição dos pedidos
- Quantidade de taxas
- Cursos
- Operador responsável
- Observações

Exemplos de uso desse comando:"errei um número no CPF" ou "cobrei um curso sem querer".

:warning: Atenção:
**Esse comando altera informações já registradas no banco de dados e nos relatórios financeiros.
Use apenas para corrigir erros e com cuidado. Alterações incorretas podem causar problemas no sistema e cobranças indevidas.**

:x: Não é possível alterar a categoria do pedido (PF/PJ).
Se um pedido foi criado e finalizado na categoria errada, contate um administrador para que o pedido seja deletado. Depois do pedido criado na categoria correta, finalize novamente.

## Excluindo pedidos

Apenas administradores podem deletar pedidos. Se é necessário deletar um pedido (se ele for criado e finalizado na categoria errada ou se precisava ter a tag :free: Gratuito para não gerar cobrança, por exemplo) contate um administrador.
""",
    "Adicionando e Removendo Tags": """
O sistema utiliza tags para saber como gerenciar os pedidos, então elas são EXTREMAMENTE IMPORTANTES para o controle financeiro. Sempre gerencie as tags de acordo com a situação do pedido.

## :free: Gratuito

Use esta tag quando o serviço **não deve ser cobrado**.

Exemplos:

- Definitivo (inclusão da primeira placa num cadastro que foi feito por nós a menos de 60 dias)
- Alterar placa para padrão mercosul (sem gerar arrendamento)
- Alteração de dados do motorista
- Exclusão
- Gerar carteirinha ou extrato

Quando um pedido PF está com essa tag, a finalização pelo botão ou pelo comando
`/feito-pf` **não cobra o serviço**.

## :red_circle: Com pendência

Use quando o pedido **não pode ser concluído** porque existe algum problema.

Pedidos com essa tag **não podem ser finalizados** até que a pendência seja resolvida.

Depois que o problema for solucionado, **remova a tag** e o operador poderá finalizar normalmente.

## :white_circle: Cancelado

Use quando o pedido **não será mais realizado**.

Pedidos cancelados **não podem ser finalizados** e **não entram nos relatórios financeiros**.

## Como adicionar ou remover uma tag

1. Abra o pedido no Fórum.
2. Na parte superior direita da postagem, clique nos três pontinhos ```...``` e então em "Editar tags".
3. Marque ou desmarque a tag desejada.
4. A alteração é salva automaticamente.
""",
    "Gerando Relatórios": """
No canal #analises, clique em um dos botões para consultar sua produção:

- **Hoje**: pedidos finalizados hoje.
- **Mês**: pedidos finalizados no mês atual.
- **Período personalizado**: informe as datas inicial e final no formato
  `dd/mm/aaaa`.

O relatório é enviado de forma privada e somente você poderá vê-lo. Apenas
operadores podem consultar o próprio relatório.

O comando `/relatorio-operador` continua disponível como alternativa e oferece
as mesmas opções de período.
""",
}


async def ensure_pinned_message(
    channel: discord.TextChannel,
    identifier: str,
    content: str,
    view: discord.ui.View | None = None,
):

    try:

        pinned_messages = await channel.pins()

        for message in pinned_messages:

            if message.author == channel.guild.me and message.content.startswith(
                identifier
            ):

                changes = {}
                if message.content != content:
                    changes["content"] = content
                if view is not None:
                    changes["view"] = view
                if changes:
                    await message.edit(**changes)

                return

        message = await channel.send(
            content,
            view=view,
        )

        await message.pin(
            reason="Configuração automática do LogoAli.",
        )

    except Exception as e:

        print(f"[ERRO][SETUP] Erro ao configurar " f"#{channel.name}: {repr(e)}")


async def get_forum_threads(
    forum: discord.ForumChannel,
):

    threads = {thread.id: thread for thread in forum.threads}

    try:

        async for thread in forum.archived_threads(
            limit=None,
        ):

            threads[thread.id] = thread

    except Exception as e:

        print(
            f"[ERRO][SETUP] Não foi possível consultar "
            f"threads arquivadas de #{forum.name}: {repr(e)}"
        )

    return list(threads.values())


async def ensure_forum_posts(
    forum: discord.ForumChannel,
):

    try:

        existing_threads = await get_forum_threads(
            forum,
        )

        existing_threads_by_title = {
            thread.name.strip().lower(): thread for thread in existing_threads
        }

        for title, content in GUIDE_POSTS.items():

            existing_thread = existing_threads_by_title.get(title.strip().lower())
            if existing_thread is not None:
                try:
                    starter_message = await existing_thread.fetch_message(
                        existing_thread.id
                    )
                    if starter_message.content != content:
                        await starter_message.edit(content=content)
                        print(
                            f"[SETUP] Tutorial atualizado | "
                            f"forum=#{forum.name} | titulo='{title}'"
                        )
                    else:
                        print(
                            f"[SETUP] Tutorial já está atualizado | "
                            f"forum=#{forum.name} | titulo='{title}'"
                        )
                except (discord.Forbidden, discord.HTTPException) as error:
                    print(
                        f"[ERRO][SETUP] Não foi possível atualizar o tutorial | "
                        f"forum=#{forum.name} | titulo='{title}' | "
                        f"erro={error!r}"
                    )
                continue

            print(
                f"[SETUP] Tutorial ausente | "
                f"forum=#{forum.name} | "
                f"criando='{title}'"
            )

            await forum.create_thread(
                name=title,
                content=content,
                auto_archive_duration=10080,
            )

            print(
                f"[SETUP] Tutorial criado | "
                f"forum=#{forum.name} | "
                f"titulo='{title}'"
            )

    except Exception as e:

        print(f"[ERRO][SETUP] Erro ao configurar " f"#{forum.name}: {repr(e)}")


async def setup_server(
    bot: discord.Client,
):

    for guild in bot.guilds:
        if guild.id not in GUILDS:
            continue

        print(
            f"[SETUP] Verificando servidor | "
            f"guild='{guild.name}' | "
            f"id={guild.id}"
        )

        # ====================================================
        # Cadastro
        # ====================================================

        registration_channel = discord.utils.get(
            guild.text_channels,
            name="cadastre-se-aqui",
        )

        if registration_channel is not None:
            await ensure_pinned_message(
                channel=registration_channel,
                identifier=REGISTRATION_ID,
                content=(
                    f"{REGISTRATION_ID}\n"
                    "# 📝 Cadastre-se\n\n"
                    "Clique no botão abaixo e escolha sua função para fazer "
                    "seu cadastro no sistema."
                ),
                view=RegisterPanelView(),
            )
        else:
            print(
                f"[SETUP] Canal #cadastre-se-aqui não encontrado | "
                f"guild='{guild.name}'"
            )

        # ====================================================
        # Boas-vindas
        # ====================================================

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

        else:

            print(f"[SETUP] Canal #bem-vindo não encontrado | " f"guild='{guild.name}'")

        # ====================================================
        # Análises
        # ====================================================

        reports_channel = discord.utils.get(
            guild.text_channels,
            name="analises",
        )

        if reports_channel is not None:

            await ensure_pinned_message(
                channel=reports_channel,
                identifier=REPORTS_ID,
                content=REPORTS_MESSAGE,
                view=OperatorReportPanelView(),
            )

        else:

            print(f"[SETUP] Canal #analises não encontrado | " f"guild='{guild.name}'")

        # ====================================================
        # Tutoriais
        # ====================================================

        guides_forum = discord.utils.get(
            guild.channels,
            name="como-usar",
        )

        if guides_forum is not None:

            await ensure_forum_posts(
                guides_forum,
            )

        else:

            print(f"[SETUP] Fórum #como-usar não encontrado | " f"guild='{guild.name}'")

        print(f"[SETUP] Verificação concluída | " f"guild='{guild.name}'")
