import discord

from commands.done import finish_order


def parse_non_negative_integer(value: str, field_name: str) -> int:
    try:
        parsed_value = int(value.strip())
    except ValueError as error:
        raise ValueError(
            f"Informe um número inteiro válido para {field_name}."
        ) from error

    if parsed_value < 0:
        raise ValueError(f"O valor de {field_name} não pode ser negativo.")

    return parsed_value


class FinishOrderDetailsModal(discord.ui.Modal):
    def __init__(self, category: str, *, user_id: int):
        super().__init__(title=f"Finalizar pedido {category.upper()}")
        self.category = category
        self.user_id = user_id

        self.client_input = discord.ui.TextInput(
            custom_id="finish_order_client",
            placeholder="Nome do cliente",
            max_length=100,
        )
        self.document_input = discord.ui.TextInput(
            custom_id="finish_order_document",
            placeholder="CPF do cliente" if category == "pf" else "CNPJ do cliente",
            max_length=30,
        )
        self.description_input = discord.ui.TextInput(
            custom_id="finish_order_description",
            placeholder="Descreva os serviços realizados",
            style=discord.TextStyle.paragraph,
            max_length=1000,
        )
        self.first_amount_input = discord.ui.TextInput(
            custom_id="finish_order_first_amount",
            placeholder=(
                "Quantidade de taxas"
                if category == "pf"
                else "Cadastros/inclusões/reativações"
            ),
            max_length=8,
        )
        self.second_amount_input = discord.ui.TextInput(
            custom_id="finish_order_second_amount",
            placeholder=(
                "Quantidade de exclusões PJ"
                if category == "pf"
                else "Alterações/exclusões"
            ),
            max_length=8,
        )

        for label, component in (
            ("Cliente", self.client_input),
            ("CPF" if category == "pf" else "CNPJ", self.document_input),
            ("Descrição dos serviços", self.description_input),
            (
                (
                    "Quantidade de taxas"
                    if category == "pf"
                    else "Cadastros/inclusões/reativações"
                ),
                self.first_amount_input,
            ),
            (
                "Exclusões PJ" if category == "pf" else "Alterações/exclusões",
                self.second_amount_input,
            ),
        ):
            self.add_item(discord.ui.Label(text=label, component=component))

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Somente quem assumiu o pedido pode preencher este formulário.",
                ephemeral=True,
            )
            return

        try:
            first_amount = parse_non_negative_integer(
                self.first_amount_input.value,
                (
                    "a quantidade de taxas"
                    if self.category == "pf"
                    else "a quantidade de cadastros"
                ),
            )
            second_amount = parse_non_negative_integer(
                self.second_amount_input.value,
                (
                    "as exclusões PJ"
                    if self.category == "pf"
                    else "as alterações/exclusões"
                ),
            )
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        await interaction.response.send_message(
            "Anexe os arquivos que ficarão disponíveis para o despachante e finalize o pedido.",
            ephemeral=True,
            view=FinishOrderContinuationView(
                category=self.category,
                user_id=interaction.user.id,
                client=self.client_input.value.strip(),
                document=self.document_input.value.strip(),
                description=self.description_input.value.strip(),
                first_amount=first_amount,
                second_amount=second_amount,
            ),
        )


class FinishOrderContinuationView(discord.ui.View):
    def __init__(
        self,
        *,
        category: str,
        user_id: int,
        client: str,
        document: str,
        description: str,
        first_amount: int,
        second_amount: int,
    ):
        super().__init__(timeout=300)
        self.category = category
        self.user_id = user_id
        self.client = client
        self.document = document
        self.description = description
        self.first_amount = first_amount
        self.second_amount = second_amount

    @discord.ui.button(
        label="Continuar e anexar arquivos",
        emoji="📎",
        style=discord.ButtonStyle.primary,
    )
    async def continue_finish_order(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Somente quem preencheu o formulário pode continuar.",
                ephemeral=True,
            )
            return

        await interaction.response.send_modal(
            FinishOrderAttachmentsModal(
                category=self.category,
                user_id=self.user_id,
                client=self.client,
                document=self.document,
                description=self.description,
                first_amount=self.first_amount,
                second_amount=self.second_amount,
            )
        )


class FinishOrderAttachmentsModal(discord.ui.Modal):
    def __init__(
        self,
        *,
        category: str,
        user_id: int,
        client: str,
        document: str,
        description: str,
        first_amount: int,
        second_amount: int,
    ):
        super().__init__(title="Dados complementares e arquivos")
        self.category = category
        self.user_id = user_id
        self.client = client
        self.document = document
        self.description = description
        self.first_amount = first_amount
        self.second_amount = second_amount

        self.courses_input = discord.ui.TextInput(
            custom_id="finish_order_courses",
            placeholder="Quantidade de cursos (padrão: 0)",
            default="0",
            required=False,
            max_length=8,
        )
        self.observations_input = discord.ui.TextInput(
            custom_id="finish_order_observations",
            placeholder="Observações (opcional)",
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=1000,
        )
        self.attachments_input = discord.ui.FileUpload(
            custom_id="finish_order_attachments",
            min_values=0,
            max_values=10,
            required=False,
        )

        self.add_item(
            discord.ui.Label(text="Quantidade de cursos", component=self.courses_input)
        )
        self.add_item(
            discord.ui.Label(
                text="Observações (opcional)",
                component=self.observations_input,
            )
        )
        self.add_item(
            discord.ui.Label(
                text="Arquivos para o despachante (opcional)",
                component=self.attachments_input,
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "Somente quem preencheu o formulário pode finalizá-lo.",
                ephemeral=True,
            )
            return

        try:
            courses = parse_non_negative_integer(
                self.courses_input.value or "0",
                "a quantidade de cursos",
            )
        except ValueError as error:
            await interaction.response.send_message(str(error), ephemeral=True)
            return

        if self.category == "pf":
            amount_fields = [
                ("Quantidade de taxas", self.first_amount),
                ("Exclusões PJ", self.second_amount),
                ("Quantidade de cursos", courses),
            ]
            create_order_kwargs = {
                "pf_amount": self.first_amount,
                "pf_exclusions_pj": self.second_amount,
                "course_amount": courses,
            }
        else:
            amount_fields = [
                ("Quantidade de Cadastros/Inclusões/Reativações", self.first_amount),
                ("Quantidade de Alterações/Exclusões", self.second_amount),
                ("Quantidade de cursos", courses),
            ]
            create_order_kwargs = {
                "pj_amount_cad_or_reval": self.first_amount,
                "pj_amount_alt_or_rem": self.second_amount,
                "course_amount": courses,
            }

        await finish_order(
            interaction=interaction,
            category=self.category,
            cliente=self.client,
            documento=self.document,
            descricao_servicos=self.description,
            operador=None,
            observacoes=self.observations_input.value.strip() or None,
            embed_title=f"✅ Pedido {self.category.upper()} finalizado",
            amount_fields=amount_fields,
            create_order_kwargs=create_order_kwargs,
            attachments=self.attachments_input.values,
            require_claimant=True,
        )
