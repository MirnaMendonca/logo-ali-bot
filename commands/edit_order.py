import discord
from discord import app_commands

from database.database import SessionLocal
from database.order_service import edit_order, get_order_by_thread_id

from google.sheets import update_order_on_sheets


class EditOrderConfirmationModal(discord.ui.Modal):

    confirmation = discord.ui.TextInput(
        label="Digite CONFIRMO para editar o pedido.",
        placeholder="⚠️ CUIDADO. Alterações podem causar cobranças erradas.",
        required=True,
        max_length=20,
    )

    def __init__(
        self,
        *,
        order_category: str,
        thread_id: str,
        cliente: str | None,
        documento: str | None,
        pedidos: str | None,
        quantidade_pf: int | None,
        exclusoes_pj: int | None,
        cadastros_inclusoes: int | None,
        alteracoes_exclusoes: int | None,
        cursos: int | None,
        operador: discord.Member | None,
        observacoes: str | None,
    ):

        super().__init__(
            title="Confirmar edição do pedido",
        )

        self.order_category = order_category
        self.thread_id = thread_id

        self.cliente = cliente
        self.documento = documento
        self.pedidos = pedidos

        self.quantidade_pf = quantidade_pf
        self.exclusoes_pj = exclusoes_pj
        self.cadastros_inclusoes = cadastros_inclusoes
        self.alteracoes_exclusoes = alteracoes_exclusoes
        self.cursos = cursos

        self.operador = operador
        self.observacoes = observacoes

    async def on_submit(
        self,
        interaction: discord.Interaction,
    ):

        if self.confirmation.value.strip().upper() != "CONFIRMO":

            await interaction.response.send_message(
                "Edição cancelada. Você deve digitar **CONFIRMO** exatamente como solicitado.",
                ephemeral=True,
            )

            return

        await interaction.response.defer(
            ephemeral=True,
        )

        session = SessionLocal()

        try:

            order = edit_order(
                session=session,
                thread_id=self.thread_id,
                client=self.cliente,
                document=self.documento,
                order_text=self.pedidos,
                pf_amount=self.quantidade_pf,
                pf_exclusions_pj=self.exclusoes_pj,
                pj_amount_cad_or_reval=self.cadastros_inclusoes,
                pj_amount_alt_or_rem=self.alteracoes_exclusoes,
                course_amount=self.cursos,
                operator_discord_id=str(self.operador.id) if self.operador else None,
                observations=self.observacoes,
            )

            update_order_on_sheets(
                order=order,
                category=self.order_category,
            )

            session.commit()

        except ValueError as e:

            session.rollback()

            await interaction.followup.send(
                str(e),
                ephemeral=True,
            )

            return

        except Exception as e:

            session.rollback()

            print(e)

            await interaction.followup.send(
                "Ocorreu um erro ao editar o pedido.",
                ephemeral=True,
            )

            return

        finally:

            session.close()

        embed = discord.Embed(
            title="✏️ Pedido editado",
            description="O pedido foi atualizado com sucesso.",
            color=discord.Color.orange(),
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )


def setup_edit_order(bot: discord.Client):

    @bot.tree.command(
        name="editar-pedido",
        description="Edita um pedido já finalizado.",
    )
    @app_commands.describe(
        cliente="Novo cliente",
        documento="Novo CPF/CNPJ",
        pedidos="Novo texto dos pedidos",
        quantidade_pf="Quantidade de taxas PF",
        exclusoes_pj="Quantidade de exclusões PJ para pedidos PF",
        cadastros_inclusoes="Quantidade de Cadastros/Inclusões/Reativações PJ",
        alteracoes_exclusoes="Quantidade de Alterações/Exclusões PJ",
        cursos="Quantidade de cursos",
        operador="Novo operador",
        observacoes="Novas observações",
    )
    async def edit_order_command(
        interaction: discord.Interaction,
        cliente: str | None = None,
        documento: str | None = None,
        pedidos: str | None = None,
        quantidade_pf: int | None = None,
        exclusoes_pj: int | None = None,
        cadastros_inclusoes: int | None = None,
        alteracoes_exclusoes: int | None = None,
        cursos: int | None = None,
        operador: discord.Member | None = None,
        observacoes: str | None = None,
    ):

        if not isinstance(
            interaction.channel,
            discord.Thread,
        ):
            await interaction.response.send_message(
                "Este comando só pode ser usado dentro de um pedido.",
                ephemeral=True,
            )
            return

        if all(
            value is None
            for value in [
                cliente,
                documento,
                pedidos,
                quantidade_pf,
                exclusoes_pj,
                cadastros_inclusoes,
                alteracoes_exclusoes,
                cursos,
                operador,
                observacoes,
            ]
        ):
            await interaction.response.send_message(
                "Você precisa informar pelo menos um campo para editar.",
                ephemeral=True,
            )
            return

        session = SessionLocal()

        try:
            order_obj = get_order_by_thread_id(
                session=session,
                thread_id=str(interaction.channel.id),
            )

            if order_obj is None:
                await interaction.response.send_message(
                    "Pedido não encontrado.",
                    ephemeral=True,
                )
                return

            order_category = order_obj.category

            if order_category == "pf":
                if (
                    cadastros_inclusoes is not None
                    or alteracoes_exclusoes is not None
                ):
                    await interaction.response.send_message(
                        "Este pedido é **PF**. Não é possível editar campos exclusivos de pedidos PJ.",
                        ephemeral=True,
                    )
                    return

            elif order_category == "pj":
                if quantidade_pf is not None or exclusoes_pj is not None:
                    await interaction.response.send_message(
                        "Este pedido é **PJ**. Não é possível editar a quantidade de taxas PF nem as exclusões PJ.",
                        ephemeral=True,
                    )
                    return

            else:
                await interaction.response.send_message(
                    "Este comando só pode ser utilizado em pedidos PF ou PJ.",
                    ephemeral=True,
                )
                return

        finally:
            session.close()

        modal = EditOrderConfirmationModal(
            order_category=order_category,
            thread_id=str(interaction.channel.id),
            cliente=cliente,
            documento=documento,
            pedidos=pedidos,
            quantidade_pf=quantidade_pf,
            exclusoes_pj=exclusoes_pj,
            cadastros_inclusoes=cadastros_inclusoes,
            alteracoes_exclusoes=alteracoes_exclusoes,
            cursos=cursos,
            operador=operador,
            observacoes=observacoes,
        )

        await interaction.response.send_modal(
            modal,
        )
