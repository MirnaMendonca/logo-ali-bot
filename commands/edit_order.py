import discord
from discord import app_commands

from database.database import SessionLocal
from database.models import User
from database.order_service import edit_order

from google.sheets import update_order_on_sheet


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
        cadastros_reativacoes: int | None,
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
        self.cadastros_reativacoes = cadastros_reativacoes
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
                category=self.order_category,
                client=self.cliente,
                document=self.documento,
                order_text=self.pedidos,
                pf_amount=self.quantidade_pf,
                pj_amount_cad_or_reval=self.cadastros_reativacoes,
                pj_amount_alt_or_rem=self.alteracoes_exclusoes,
                course_amount=self.cursos,
                operator_discord_id=str(self.operador.id) if self.operador else None,
                observations=self.observacoes,
            )

            update_order_on_sheet(
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
        cadastros_reativacoes="Quantidade de Cadastros/Reativações PJ",
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
        cadastros_reativacoes: int | None = None,
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
                cadastros_reativacoes,
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

        forum = interaction.channel.parent

        if forum is None:
            await interaction.response.send_message(
                "Não foi possível identificar a categoria do pedido.",
                ephemeral=True,
            )
            return

        if "pf" in forum.name.lower():

            order_category = "pf"

            if cadastros_reativacoes is not None or alteracoes_exclusoes is not None:
                await interaction.response.send_message(
                    "Este pedido é **PF**. Não é possível editar campos exclusivos de pedidos PJ.",
                    ephemeral=True,
                )
                return

        elif "pj" in forum.name.lower():

            order_category = "pj"

            if quantidade_pf is not None:
                await interaction.response.send_message(
                    "Este pedido é **PJ**. Não é possível editar a quantidade de taxas PF.",
                    ephemeral=True,
                )
                return

        else:

            await interaction.response.send_message(
                "Este comando só pode ser utilizado em pedidos PF ou PJ.",
                ephemeral=True,
            )
            return

        modal = EditOrderConfirmationModal(
            order_category=order_category,
            thread_id=str(interaction.channel.id),
            cliente=cliente,
            documento=documento,
            pedidos=pedidos,
            quantidade_pf=quantidade_pf,
            cadastros_reativacoes=cadastros_reativacoes,
            alteracoes_exclusoes=alteracoes_exclusoes,
            cursos=cursos,
            operador=operador,
            observacoes=observacoes,
        )

        await interaction.response.send_modal(
            modal,
        )
