import discord
from datetime import datetime
from database_reports.operations import create_report
from config import REPORT_CHANNEL_ID
from .views import ReportModerationView

class ReportModal(discord.ui.Modal, title="Подать жалобу"):
    def __init__(self, user: discord.User, bot):
        super().__init__(timeout=300)
        self.target_user = user  # пользователь, на которого жалоба
        self.bot = bot
        
    report_description_input = discord.ui.TextInput(
        label='Причина жалобы',
        placeholder='Кратко опишите вашу жалобу...',
        max_length=200,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Сохраняем в базу данных
        report = create_report(
            user_id=str(interaction.user.id),
            user_name=interaction.user.display_name,
            target_user_id=str(self.target_user.id),
            target_user_name=self.target_user.display_name,
            report_description=self.report_description_input.value
        )
        
        # Отправляем в канал модерации
        mod_channel = self.bot.get_channel(REPORT_CHANNEL_ID)
        if mod_channel:
            
            embed = discord.Embed(
                title="📝 Новая жалоба",
                description=self.report_description_input.value,
                color=0xf39c12,
                timestamp=datetime.now()
            )
            embed.add_field(name="👤 От кого", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="👤 На кого", value=f"{self.target_user.mention}", inline=True)
            embed.set_footer(text=f"ID: {report.id} • Ожидание модерации")
            
            view = ReportModerationView(
               report_id=report.id,
               bot=self.bot,
               target_user_id=self.target_user.id,
               target_user_name=self.target_user.display_name
            )
            await mod_channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(
            f"✅ Ваша жалоба на {self.target_user.mention} отправлена на модерацию!",
            ephemeral=True,
            delete_after=10
        )