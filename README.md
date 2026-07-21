# LogoAli Bot

Bot para Discord desenvolvido para automatizar o fluxo de trabalho entre despachantes e operadores, substituindo grupos de WhatsApp por um ambiente organizado, com controle financeiro, relatórios e integração com Google Sheets.

O projeto foi desenvolvido pensando em múltiplos servidores, permitindo que cada despachante possua seu próprio servidor Discord enquanto utiliza a mesma base de código.

## Funcionalidades

Gerenciamento de pedidos utilizando Fóruns do Discord

Status por tags: Aguardando, Em andamento, Finalizado, Cancelado, Com pendência, Gratuito

Botão para assumir pedidos e bloqueio para impedir dois operadores trabalhando no mesmo pedido

Relatórios financeiros para operadores, despachantes e geral com permissionamento

Integração automática com as planilhas do Google para visualização dos pedidos

## Cadastro de usuários

Cada usuário realiza seu próprio cadastro através do Discord.

Existem dois tipos de usuário: Despachante ou Operador

O cadastro também registra o usuário no banco de dados utilizado para geração dos relatórios.

## Finalização de pedidos

Existem dois comandos independentes:

```/feito-pf```

```/feito-pj```

Ao finalizar um pedido o bot:

- valida o pedido

- calcula automaticamente os valores

- salva no banco de dados

- envia para o Google Sheets

- altera a tag para Finalizado

- gera um resumo da operação

Pedidos podem ser enviados diretamente para revisão quando necessário.

## Relatórios

O sistema possui três tipos de relatório, que podem ser consultados nos períodos "hoje", "mês" e "período personalizado".
Os relatórios são privados e, com exceção do relatório geral, não pode ser lido por ninguém além da pessoa que enviou o comando.

### Relatório do operador

```/relatorio-operador```

Mostra:

- quantidade de pedidos

- valor acumulado

### Relatório do despachante

```/relatorio-despachante```

Mostra:

- quantidade de pedidos PF

- quantidade de pedidos PJ

- quantidade de cursos

- valor dos pedidos PF e cursos

- valor dos pedidos PJ

- valor líquido

### Relatório geral

```/relatorio-geral```

Disponível apenas para administradores e enviado automaticamente todos os dias em um canal de texto privado.

Mostra:

- quanto cobrar do despachante no dia

- quanto pagar para cada operador na semana atual

- total da folha de pagamento dos operadores

## Relatórios automáticos

Todos os dias o bot envia automaticamente um relatório no canal #relatorios

Na sexta-feira também envia o fechamento semanal dos operadores.

Isso cria um histórico permanente dentro do próprio Discord que é acessível apenas aos administradores.

## Integração com Google Sheets

Pedidos são enviados automaticamente para planilhas.

Cada servidor utiliza suas próprias abas.

Pedidos enviados para revisão vão para a aba "revisão".

## Controle financeiro

O sistema calcula automaticamente os valores de cada serviço para o despachante e para o operador.

Todos os valores são configuráveis.

## Tecnologias
Python 3.13

discord.py

SQLAlchemy

SQLite

Google Sheets API

gspread

python-dotenv

## Configuração

Necessário criar o arquivo .env com o Token do Discord e o arquivo .json de acesso do Google Sheets, além de configurar quaisquer valores novos em config.py

## Executando

Instale as dependências

pip install -r requirements.txt

Execute

python main.py

## Objetivos do projeto

Este bot foi criado para substituir um fluxo totalmente manual realizado através de grupos de WhatsApp.

Os principais objetivos são:

- organização dos pedidos

- redução de erros humanos

- cálculo automático dos pagamentos

- geração de relatórios

- integração com Google Sheets

- histórico permanente

- suporte a múltiplos despachantes utilizando o mesmo sistema

 
## Licença

Este projeto foi desenvolvido para uso interno da LogoAli e não possui licença pública definida.
