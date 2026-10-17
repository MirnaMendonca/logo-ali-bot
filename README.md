# LogoAli Bot

Bot para Discord desenvolvido para automatizar o fluxo de trabalho entre despachantes e operadores, substituindo grupos de WhatsApp por um ambiente organizado, com controle financeiro, relatórios e integração com Google Sheets.

O projeto foi desenvolvido pensando em múltiplos servidores, permitindo que cada despachante possua seu próprio servidor Discord enquanto utiliza a mesma base de código.

## Funcionalidades

Gerenciamento de pedidos utilizando Fóruns do Discord

Status por tags: Aguardando, Em andamento, Finalizado, Cancelado, Com pendência, Gratuito

Botão para assumir pedidos e bloqueio para impedir dois operadores trabalhando no mesmo pedido

Relatórios financeiros para operadores e administradores, com permissionamento

Integração automática com as planilhas do Google para visualização dos pedidos

## Cadastro de usuários

Cada usuário realiza seu próprio cadastro através do Discord.

Existem dois tipos de usuário: Despachante ou Operador

O cadastro também registra o usuário no banco de dados utilizado para geração dos relatórios.

## Finalização de pedidos

Nos pedidos PF/PJ, o operador pode assumir o pedido pelo botão e, em seguida,
clicar em **Finalizar pedido** para preencher o formulário da categoria correta.
Somente quem assumiu pode usar o botão de finalização; os comandos slash continuam
livres e registram como operador quem assumiu o pedido.
O formulário permite anexar até 10 arquivos; eles ficam na mensagem de
finalização dentro do tópico, disponíveis para o despachante baixar. Os comandos
slash abaixo continuam disponíveis como alternativa.

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

- permite registrar a devolução escolhendo um nome no menu: Administração, Kauan, João, Sophia ou Alana; o nome escolhido também é enviado à planilha do despachante

Pedidos podem ser enviados diretamente para revisão quando necessário.

## Relatórios

O sistema possui relatório de produção para operadores, que pode ser consultado nos períodos "hoje", "mês" e "período personalizado", e relatório geral para administradores.
Os relatórios são privados e, com exceção do relatório geral, não podem ser lidos por ninguém além da pessoa que enviou o comando.

### Análise de planilha

O comando `/analisar-planilha`, disponível apenas para administradores, recebe relatórios e envia uma planilha privada com análises relevantes.

### Relatório do operador

```/relatorio-operador```

Mostra:

- quantidade de pedidos

- valor acumulado

### Relatório geral

```/relatorio-geral```

Disponível apenas para administradores e enviado automaticamente todos os dias em um canal de texto privado.

Mostra:

- quanto cobrar do despachante no dia

- quanto pagar para cada operador na semana atual

- total da folha de pagamento dos operadores

## Relatórios automáticos

Todos os dias às 20h o bot envia automaticamente o fechamento diário nos canais de relatório. Cada fechamento considera os pedidos concluídos entre 20h do dia anterior (inclusive) e 20h do dia do fechamento (exclusive). Assim, pedidos concluídos após as 20h entram no fechamento do dia seguinte.

Na sexta-feira também envia o fechamento semanal dos operadores.

Ao reiniciar, o bot confere o histórico do dia nos canais e não reenvia as partes do fechamento que já foram publicadas.

Isso cria um histórico permanente dentro do próprio Discord que é acessível apenas aos administradores.

## Integração com Google Sheets

Pedidos são enviados automaticamente para planilhas.

Cada servidor utiliza suas próprias abas.

Pedidos enviados para revisão vão para a aba "revisão".

Pedidos PF com exclusões PJ também são copiados para a aba `exclusoes-pj` da planilha do despachante, com os mesmos dados da aba `pf`.

Pedidos PF marcados como gratuitos são registrados no banco de dados com os campos numéricos zerados e também na planilha principal. Eles não entram nos totais financeiros nem nas abas PF/PJ de pedidos pagos.

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
