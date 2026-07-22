import discord
from discord import app_commands

from commands.done import finish_order


def setup_done_pj(bot: discord.Client):

    @bot.tree.command(
        name="feito-pj",
        description="Finaliza um pedido PJ.",
    )
    @app_commands.describe(
        cliente="Nome do cliente",
        cnpj="CNPJ do cliente",
        pedidos="Pedidos realizados",
        cadastros_reativacoes="Quantidade de Cadastros/Inclusões/Reativações",
        alteracoes_exclusoes="Quantidade de Alterações/Exclusões",
        cursos="Quantidade de cursos feitos (RT ou TAC)",
        observacoes="Observações (opcional)",
        revisao="Enviar para revisão?",
        operador="Operador (opcional)",
    )
    async def done_pj(
        interaction: discord.Interaction,
        cliente: str,
        cnpj: str,
        pedidos: str,
        cadastros_reativacoes: int,
        alteracoes_exclusoes: int,
        cursos: int,
        observacoes: str | None = None,
        revisao: bool = False,
        operador: discord.Member | None = None,
    ):

        await finish_order(
            interaction=interaction,
            category="pj",
            cliente=cliente,
            documento=cnpj,
            pedidos=pedidos,
            operador=operador,
            revisao=revisao,
            observacoes=observacoes,
            embed_title="✅ Pedido PJ finalizado",
            amount_fields=[
                (
                    "Quantidade de Cadastros/Inclusões/Reativações",
                    cadastros_reativacoes,
                ),
                (
                    "Quantidade de Alterações/Exclusões",
                    alteracoes_exclusoes,
                ),
                (
                    "Quantidade de cursos",
                    cursos,
                ),
            ],
            create_order_kwargs={
                "pj_amount_cad_or_reval": cadastros_reativacoes,
                "pj_amount_alt_or_rem": alteracoes_exclusoes,
                "course_amount": cursos,
            },
        )
