import discord
from datetime import datetime
from database_reports.operations import create_report
from config import REPORT_CHANNEL_ID
from .views import ReportModerationView

class ReportModal(discord.ui.Modal, title="Подать жалобу"):
    def __init__(self, user: discord.User, bot):
        super().__init__(timeout=300)
        self.target_user = user
        self.bot = bot
        
    report_description_input = discord.ui.TextInput(
        label='Причина жалобы',
        placeholder='Кратко опишите вашу жалобу...',
        max_length=200,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"🔍 [DEBUG] Начало обработки модалки")
            print(f"🔍 [DEBUG] Пользователь: {interaction.user} ({interaction.user.id})")
            print(f"🔍 [DEBUG] Целевой пользователь: {self.target_user} ({self.target_user.id})")
            print(f"🔍 [DEBUG] Текст жалобы: {self.report_description_input.value}")
            
            # Проверяем данные перед сохранением
            if not self.report_description_input.value.strip():
                await interaction.response.send_message("❌ Текст жалобы не может быть пустым!", ephemeral=True)
                return
            
            print(f"🔍 [DEBUG] Сохранение в БД...")
            
            # Сохраняем в базу данных
            report = create_report(
                user_id=str(interaction.user.id),
                user_name=interaction.user.display_name,
                target_user_id=str(self.target_user.id),
                target_user_name=self.target_user.display_name,
                report_description=self.report_description_input.value
            )
            
            print(f"🔍 [DEBUG] Жалоба сохранена, ID: {report.id if report else 'NONE'}")
            
            if not report:
                await interaction.response.send_message("❌ Ошибка сохранения жалобы в базу", ephemeral=True)
                return
            
            print(f"🔍 [DEBUG] Канал модерации ID: {REPORT_CHANNEL_ID}")
            
            # Отправляем в канал модерации
            mod_channel = self.bot.get_channel(int(REPORT_CHANNEL_ID))
            print(f"🔍 [DEBUG] Найденный канал: {mod_channel}")
            
            if mod_channel:
                print(f"🔍 [DEBUG] Создание embed...")
                embed = discord.Embed(
                    title="📝 Новая жалоба",
                    description=self.report_description_input.value,
                    color=0xf39c12,
                    timestamp=datetime.now()
                )
                embed.add_field(name="👤 От кого", value=f"{interaction.user.mention}", inline=True)
                embed.add_field(name="👤 На кого", value=f"{self.target_user.mention}", inline=True)
                embed.set_footer(text=f"ID: {report.id} • Ожидание модерации")
                
                print(f"🔍 [DEBUG] Создание view...")
                view = ReportModerationView(
                   report_id=report.id,
                   bot=self.bot,
                   target_user_id=self.target_user.id,
                   target_user_name=self.target_user.display_name
                )
                
                print(f"🔍 [DEBUG] Отправка в канал...")
                await mod_channel.send(embed=embed, view=view)
                print(f"🔍 [DEBUG] Сообщение отправлено в канал")
            
            print(f"🔍 [DEBUG] Отправка ответа пользователю...")
            await interaction.response.send_message(
                f"✅ Ваша жалоба на {self.target_user.mention} отправлена на модерацию!",
                ephemeral=True,
                delete_after=10
            )
            print(f"🔍 [DEBUG] Успешно завершено!")
            
        except Exception as e:
            print(f"❌ [ERROR] Критическая ошибка в модалке: {e}")
            print(f"❌ [ERROR] Тип ошибки: {type(e)}")
            import traceback
            traceback.print_exc()
            
            try:
                await interaction.response.send_message(
                    f"❌ Произошла ошибка при отправке жалобы. Попробуйте позже.",
                    ephemeral=True,
                    delete_after=10
                )
            except:
                # Если уже ответили
                await interaction.followup.send(
                    "❌ Произошла ошибка при отправке жалобы",
                    ephemeral=True,
                    delete_after=10
                )