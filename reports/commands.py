import discord
from discord import app_commands
from .modals import ReportModal

def setup_report_commands(bot):
    """Регистрация команд для системы жалоб"""

    @bot.tree.command(name="report", description="Подать жалобу")
    @app_commands.describe(
        user="Пользователь, на которого подается жалоба"
    )
    async def report_slash(interaction: discord.Interaction, user: discord.User):
        """Вызывает модальное окно для жалобы"""
        modal = ReportModal(user=user, bot=bot)
        await interaction.response.send_modal(modal)