import discord

from commands.register import register_user
from commands.report_operator import send_operator_report
from config import USER_ROLES


class RegisterRoleView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

        class RoleSelect(discord.ui.Select):
            def __init__(self):
                super().__init__(
                    placeholder="Selecione sua função",
                    custom_id="register_role_selection",
                    options=[
                        discord.SelectOption(
                            label=USER_ROLES["dispatcher"],
                            value="dispatcher",
                        ),
                        discord.SelectOption(
                            label=USER_ROLES["operator"],
                            value="operator",
                        ),
                    ],
                    min_values=1,
                    max_values=1,
                )

            async def callback(self, interaction: discord.Interaction):
                await register_user(interaction, self.values[0])

        self.add_item(RoleSelect())


class RegisterPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Fazer meu cadastro",
        emoji="📝",
        style=discord.ButtonStyle.primary,
        custom_id="register_panel_open",
    )
    async def open_registration(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_message(
            "Escolha sua função para realizar o cadastro:",
            view=RegisterRoleView(),
            ephemeral=True,
        )


class CustomOperatorReportModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Relatório por período")
        self.start_date = discord.ui.TextInput(
            custom_id="operator_report_start_date",
            placeholder="dd/mm/aaaa",
            max_length=10,
        )
        self.end_date = discord.ui.TextInput(
            custom_id="operator_report_end_date",
            placeholder="dd/mm/aaaa",
            max_length=10,
        )
        self.add_item(
            discord.ui.Label(
                text="Data inicial",
                component=self.start_date,
            )
        )
        self.add_item(
            discord.ui.Label(
                text="Data final",
                component=self.end_date,
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        await send_operator_report(
            interaction,
            period="custom",
            start_date_value=self.start_date.value.strip(),
            end_date_value=self.end_date.value.strip(),
        )


class OperatorReportPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Hoje",
        emoji="📅",
        style=discord.ButtonStyle.primary,
        custom_id="operator_report_today",
    )
    async def report_today(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await send_operator_report(interaction, period="today")

    @discord.ui.button(
        label="Mês",
        emoji="🗓️",
        style=discord.ButtonStyle.primary,
        custom_id="operator_report_month",
    )
    async def report_month(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await send_operator_report(interaction, period="month")

    @discord.ui.button(
        label="Período personalizado",
        emoji="🔎",
        style=discord.ButtonStyle.secondary,
        custom_id="operator_report_custom",
    )
    async def report_custom(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        await interaction.response.send_modal(CustomOperatorReportModal())
