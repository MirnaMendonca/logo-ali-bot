import discord
from discord import app_commands

from commands.done import finish_order


def setup_done_pf(bot: discord.Client):

    @bot.tree.command(
        name="feito-pf",
        description="Finaliza um pedido PF.",
    )
    @app_commands.describe(
        cliente="Nome do cliente",
        cpf="CPF do cliente",
        pedidos="Pedidos realizados. Ex: TAC + Cadastro",
        quantidade="Quantidade de taxas cobradas. Ex: um cadastro com duas placas são duas taxas",
        cursos="Quantidade de cursos feitos (RT ou TAC)",
        observacoes="Observações (opcional)",
        operador="Operador (opcional)",
    )
    async def done_pf(
        interaction: discord.Interaction,
        cliente: str,
        cpf: str,
        pedidos: str,
        quantidade: int,
        cursos: int,
        observacoes: str | None = None,
        operador: discord.Member | None = None,
    ):

        await finish_order(
            interaction=interaction,
            category="pf",
            cliente=cliente,
            documento=cpf,
            pedidos=pedidos,
            operador=operador,
            observacoes=observacoes,
            embed_title="✅ Pedido PF finalizado",
            amount_fields=[
                (
                    "Quantidade de taxas",
                    quantidade,
                ),
                (
                    "Quantidade de cursos",
                    cursos,
                ),
            ],
            create_order_kwargs={
                "pf_amount": quantidade,
                "course_amount": cursos,
            },
        )
