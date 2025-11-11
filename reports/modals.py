import discord
from datetime import datetime
from database_reports.operations import create_report
from config import REPORT_CHANNEL_ID
from .views import ReportModerationView

class ReportModal(discord.ui.Modal, title="Подать жалобу"):
    def __init__(self, target_user: discord.User, bot):
        super().__init__(timeout=300)
        self.target_user = target_user
        self.bot = bot
        
    report_description_input = discord.ui.TextInput(
        label='Причина жалобы',
        placeholder='Кратко опишите вашу жалобу...',
        max_length=200,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"🔍 [DEBUG] Модалка отправлена пользователем {interaction.user}")
            
            # Сохраняем в базу данных
            report = create_report(
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                target_user_id=str(self.target_user.id),
                target_user_name=self.target_user.display_name,
                report_description=self.report_description_input.value
            )
            
            print(f"🔍 [DEBUG] Жалоба сохранена с ID: {report.id}")
            
            # Отправляем в канал модерации
            mod_channel = self.bot.get_channel(REPORT_CHANNEL_ID)
            if mod_channel:
                embed = discord.Embed(
                    title="📝 Новая жалоба",
                    description=self.report_description_input.value,
                    color=0xf39c12,  # оранжевый цвет для ожидания
                    timestamp=datetime.now()
                )
                embed.add_field(name="👤 От кого", value=f"{interaction.user.mention}", inline=True)
                embed.add_field(name="👤 На кого", value=f"{self.target_user.mention}", inline=True)
                embed.add_field(name="🆔 ID жалобы", value=f"`{report.id}`", inline=True)
                embed.set_footer(text="⏳ Ожидание модерации")
                
                view = ReportModerationView(
                   report_id=report.id,
                   bot=self.bot,
                   target_user_id=self.target_user.id,
                   target_user_name=self.target_user.display_name
                )
                
                await mod_channel.send(embed=embed, view=view)
                print(f"🔍 [DEBUG] Сообщение отправлено в канал модерации")
            
            # Отправляем подтверждение пользователю
            await interaction.response.send_message(
                f"✅ Ваша жалоба на {self.target_user.mention} отправлена на модерацию!",
                ephemeral=False
            )
            
        except Exception as e:
            print(f"❌ [ERROR] Ошибка в модалке: {e}")
            import traceback
            traceback.print_exc()
            
            await interaction.response.send_message(
                "❌ Произошла ошибка при отправке жалобы. Попробуйте позже.",
                ephemeral=True,
                delete_after=10
            )