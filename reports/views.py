import discord
from datetime import datetime
from database_reports.operations import update_report_status

class ReportModerationView(discord.ui.View):
    def __init__(self, report_id: int, bot, target_user_id: int, target_user_name: str):
        super().__init__(timeout=None)
        self.report_id = report_id
        self.bot = bot
        self.target_user_id = target_user_id
        self.target_user_name = target_user_name
    
    @discord.ui.button(label='Принять', style=discord.ButtonStyle.success, emoji='✅', custom_id='approve_report')
    async def approve_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Обновляем статус в базе
        report = update_report_status(self.report_id, 'approved', str(interaction.user.id))
        
        if report:
            # Обновляем Embed
            embed = discord.Embed(
                title="✅ Жалоба ПРИНЯТА",
                description=report.report_description,
                color=0x2ecc71,  # зеленый
                timestamp=datetime.now()
            )
            embed.add_field(name="👤 От кого", value=f"<@{interaction.user.id}>", inline=True)
            embed.add_field(name="👤 На кого", value=f"<@{self.target_user_id}>", inline=True)
            embed.add_field(name="👨‍💼 Модератор", value=f"{interaction.user.mention}", inline=True)
            embed.set_footer(text=f"🆔 ID: {report.id} • Принято {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message('✅ Жалоба принята!', ephemeral=True, delete_after=10)
    
    @discord.ui.button(label='Отклонить', style=discord.ButtonStyle.danger, emoji='❌', custom_id='reject_report')
    async def reject_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Обновляем статус в базе
        report = update_report_status(self.report_id, 'rejected', str(interaction.user.id))
        
        if report:
            # Обновляем Embed
            embed = discord.Embed(
                title="❌ Жалоба ОТКЛОНЕНА",
                description=report.report_description,
                color=0xe74c3c,  # красный
                timestamp=datetime.now()
            )
            embed.add_field(name="👤 От кого", value=f"<@{interaction.user.id}>", inline=True)
            embed.add_field(name="👤 На кого", value=f"<@{self.target_user_id}>", inline=True)
            embed.add_field(name="👨‍💼 Модератор", value=f"{interaction.user.mention}", inline=True)
            embed.set_footer(text=f"🆔 ID: {report.id} • Отклонено {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message('❌ Жалоба отклонена!', ephemeral=True, delete_after=10)