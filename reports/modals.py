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
        print(f"🔍 [REPORT MODAL] Инициализирована для {target_user}")
        
    report_description_input = discord.ui.TextInput(
        label='Причина жалобы',
        placeholder='Кратко опишите вашу жалобу...',
        max_length=200,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        print(f"🔍 [REPORT MODAL] on_submit начат")
        
        try:
            # ДЕФЕРИМ ОТВЕТ сразу
            await interaction.response.defer(ephemeral=True, thinking=True)
            print(f"🔍 [REPORT MODAL] Ответ отложен")
            
            # 1. Сохраняем в базу
            print(f"🔍 [REPORT MODAL] Сохраняем в БД...")
            report = create_report(
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                target_user_id=str(self.target_user.id),
                target_user_name=self.target_user.display_name,
                report_description=self.report_description_input.value
            )
            print(f"✅ [REPORT MODAL] Жалоба сохранена с ID: {report.id}")
            
            # 2. Отправляем в канал модерации
            print(f"🔍 [REPORT MODAL] Ищем канал {REPORT_CHANNEL_ID}")
            mod_channel = self.bot.get_channel(REPORT_CHANNEL_ID)
            print(f"🔍 [REPORT MODAL] Канал: {mod_channel}")
            
            if mod_channel:
                print(f"🔍 [REPORT MODAL] Создаем embed...")
                embed = discord.Embed(
                    title="📝 Новая жалоба",
                    description=self.report_description_input.value,
                    color=0xf39c12,
                    timestamp=datetime.now()
                )
                embed.add_field(name="👤 От кого", value=f"{interaction.user.mention}", inline=True)
                embed.add_field(name="👤 На кого", value=f"{self.target_user.mention}", inline=True)
                embed.set_footer(text=f"ID: {report.id} • Ожидание модерации")
                
                print(f"🔍 [REPORT MODAL] Создаем View...")
                view = ReportModerationView()
                
                print(f"🔍 [REPORT MODAL] Отправляем в канал...")
                await mod_channel.send(embed=embed, view=view)
                print(f"✅ [REPORT MODAL] Сообщение отправлено в канал")
            else:
                print(f"❌ [REPORT MODAL] Канал не найден!")
            
            # 3. Отправляем ответ пользователю
            print(f"🔍 [REPORT MODAL] Отправляем ответ пользователю...")
            await interaction.followup.send(
                f"✅ Ваша жалоба на {self.target_user.mention} отправлена!",
                ephemeral=True,
            )
            print(f"✅ [REPORT MODAL] Все завершено успешно")
            
        except Exception as e:
            print(f"❌ [REPORT MODAL] Критическая ошибка: {e}")
            import traceback
            traceback.print_exc()
            
            await interaction.followup.send(
                "❌ Ошибка при отправке жалобы",
                ephemeral=True,
            )

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        print(f"❌ [REPORT MODAL] Глобальная ошибка: {error}")
        import traceback
        traceback.print_exc()
        
        await interaction.followup.send(
            "❌ Непредвиденная ошибка",
            ephemeral=True,
        )