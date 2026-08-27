import discord

WELCOME_ID = "Boas-vindas"
REPORTS_ID = "Análises"


WELCOME_MESSAGE = f"""{WELCOME_ID}
# 👋 Bem-vindo(a) ao LogoAli!

Para começar a utilizar o sistema, você precisa fazer seu cadastro.
Vá no canal #cadastre-se-aqui logo abaixo desse canal e digite o comando:
```/cadastrar```

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

## 👨‍💼 Operadores

### `/relatorio-operador`

---
## 🏢 Despachantes

### `/relatorio-despachante`

"""


# ============================================================
# Tutoriais do fórum #como-usar
# ============================================================

GUIDE_POSTS = {
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
Clique no botão :arrow_forward: Assumir pedido
O sistema irá marcar como :blue_circle: Em andamento e vai mostrar que o pedido está com você.
Enquanto isso outro operador não conseguirá assumir o mesmo pedido.

## 2. Devolver um serviço

Caso tenha assumido por engano ou não consiga realizar o serviço, clique novamente no botão.
O pedido voltará para :yellow_circle: Aguardando e outro operador poderá assumir.

## 3. Regras importantes

:white_check_mark: Sempre assuma o pedido antes de começar, para que não haja confusões sobre qual operador está fazendo o pedido.

:white_check_mark: Respeite sempre que o nome que aparecer no botão é o do operador que assumiu primeiro o pedido. Se seu nome não estiver no botão, não faça o pedido, a não ser em exceções onde o operador original não conseguiu devolver o pedido mas não vai conseguir completá-lo também.

:white_check_mark: Da mesma forma, se não conseguir completar um pedido, devolva-o.
""",
    "Guia do Operador - Finalizando Pedidos": """
## 1. Finalizando um serviço

Depois de enviar a documentação necessária:

### Em pedidos PF
utilize ```/feito-pf```

Preencha:

- cliente: Nome do cliente
- CPF: CPF do cliente
- pedidos: Tipo de serviço realizado. Descreva o que foi feito, por exemplo: "TAC + Cadastro" ou "Mercosul com arrendamento"
- quantidade: Quantidade de taxas cobradas. Por exemplo: um cadastro com 3 placas são 3 taxas, inclusão de 2 placas são 2 taxas.
- cursos: Quantidade de cursos, RT ou TAC, realizados. Se não tiver feito um curso, preencha com 0 

### Em pedidos PJ
utilize ```/feito-pj```

Preencha:

- cliente: Nome do cliente
- CNPJ: CNPJ do cliente
- pedidos: Tipo de serviço realizado. Descreva o que foi feito, por exemplo: "Alteração + Exclusão" ou "Cadastro + 3 Inclusões"
- cadastros_reativacoes: Quantidade de serviços que são Cadastros, Reativações ou Inclusões.
- alteracoes_exclusoes: Quantidade de serviços que são Alterações ou Exclusões.
- cursos: Quantidade de cursos, RT ou TAC, realizados. Se não tiver feito um curso, preencha com 0 

## 2. Pedido gratuito

Se o pedido possuir a tag :free: Gratuito finalize-o normalmente. Ele não será contabilizado financeiramente.

## Parâmetros opcionais
 Além dos campos obrigatórios, também é possível enviar outras informações ao finalizar um pedido.
### observacoes
Utilize para adicionar quaisquer observações que sejam importantes no pedido. Lembre-se: ele ainda será contabilizado se não for um pedido gratuito.
### operador
Indique que outro operador fez o pedido. O pedido será dado como feito por ele e não por você. Serve para finalizar pedidos que o operador responsável não pode finalizar no momento por algum motivo.

## Regras importantes

:white_check_mark: Não finalize pedidos incompletos. Envie a documentação necessária antes de finalizar o pedido.

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

Quando um pedido está com essa tag, o comando `/feito-pf` ou `/feito-pj` **não cobra o serviço**.

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
Você pode consultar sua produção utilizando:
```/relatorio-operador``` ou ```/relatorio-despachante```
É possível visualizar:
- Hoje
- Mês
- Período personalizado

:white_check_mark: É recomendável usar o canal #analises  pra isso

:white_check_mark: Só você vai poder ver o relatório, mais ninguém
""",
}


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

        existing_titles = {thread.name.strip().lower() for thread in existing_threads}

        for title, content in GUIDE_POSTS.items():

            if title.strip().lower() in existing_titles:

                print(
                    f"[SETUP] Tutorial já existe | "
                    f"forum=#{forum.name} | "
                    f"titulo='{title}'"
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

        print(
            f"[SETUP] Verificando servidor | "
            f"guild='{guild.name}' | "
            f"id={guild.id}"
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
