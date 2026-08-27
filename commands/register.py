import discord
from discord import app_commands

from database.database import SessionLocal
from database.models import User

from config import USER_ROLES


async def role_autocomplete(
    interaction: discord.Interaction,
    current: str,
):

    allowed_roles = (
        "dispatcher",
        "operator",
    )

    return [
        app_commands.Choice(
            name=USER_ROLES[key],
            value=key,
        )
        for key in allowed_roles
        if current.lower() in USER_ROLES[key].lower()
    ]


def setup_register(bot: discord.Client):

    @bot.tree.command(
        name="cadastrar",
        description="Realiza seu cadastro no sistema.",
    )
    @app_commands.describe(
        role="Função",
    )
    @app_commands.autocomplete(
        role=role_autocomplete,
    )
    async def register(
        interaction: discord.Interaction,
        role: str,
    ):

        if role not in (
            "dispatcher",
            "operator",
        ):

            await interaction.response.send_message(
                "Função inválida.",
                ephemeral=True,
            )

            return

        session = SessionLocal()

        try:

            existing_user = (
                session.query(User)
                .filter_by(
                    discord_id=str(interaction.user.id),
                )
                .first()
            )

            if existing_user:

                if existing_user.role != role:

                    await interaction.response.send_message(
                        (
                            f"Você já está cadastrado como "
                            f"**{USER_ROLES[existing_user.role]}**. "
                            "Não é possível alterar sua função."
                        ),
                        ephemeral=True,
                    )

                    return

                user_role = discord.utils.get(
                    interaction.guild.roles,
                    name=USER_ROLES[existing_user.role],
                )

                if user_role is None:

                    await interaction.response.send_message(
                        (
                            f"O cargo **{USER_ROLES[existing_user.role]}** "
                            "não foi encontrado neste servidor. "
                            "Contate um administrador."
                        ),
                        ephemeral=True,
                    )

                    return

                if user_role not in interaction.user.roles:

                    await interaction.user.add_roles(
                        user_role,
                    )

                    await interaction.response.send_message(
                        (
                            f"Você já estava cadastrado como "
                            f"**{USER_ROLES[existing_user.role]}**, "
                            "e o cargo foi adicionado neste servidor."
                        ),
                        ephemeral=True,
                    )

                    return

                await interaction.response.send_message(
                    (
                        f"Você já está cadastrado como "
                        f"**{USER_ROLES[existing_user.role]}** "
                        "e já possui o cargo neste servidor."
                    ),
                    ephemeral=True,
                )

                return

            user = User(
                discord_id=str(interaction.user.id),
                name=interaction.user.display_name,
                role=role,
            )

            discord_role = discord.utils.get(
                interaction.guild.roles,
                name=USER_ROLES[role],
            )

            if discord_role is None:

                await interaction.response.send_message(
                    (
                        f"O cargo **{USER_ROLES[role]}** "
                        "não foi encontrado neste servidor. "
                        "Contate um administrador."
                    ),
                    ephemeral=True,
                )

                return

            session.add(user)
            session.commit()

            await interaction.user.add_roles(
                discord_role,
            )

            embed = discord.Embed(
                title="✅ Cadastro realizado",
                description=(f"Você foi cadastrado como **{USER_ROLES[role]}**."),
                color=discord.Color.green(),
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True,
            )

        except Exception:

            session.rollback()
            raise

        finally:

            session.close()
