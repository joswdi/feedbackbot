import discord
from datetime import datetime
from database_feedback.operations import create_feedback
from config import FEEDBACK_CHANNEL_ID

class FeedbackModal(discord.ui.Modal, title='Оставить отзыв'):
    def __init__(self, channel, pin_service, bot):
        super().__init__(timeout=300)
        self.channel = channel
        self.pin_service = pin_service
        self.bot = bot
    
    title_input = discord.ui.TextInput(
        label='Заголовок отзыва',
        placeholder='Кратко опишите ваш отзыв...',
        max_length=200,
        required=True
    )
    
    message_input = discord.ui.TextInput(
        label='Текст отзыва',
        placeholder='Подробно опишите ваш опыт... Что понравилось? Что можно улучшить?',
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=True
    )
    
    rating_input = discord.ui.TextInput(
        label='Оценка (от 1 до 5)',
        placeholder='Введите число от 1 до 5, где 5 - отлично',
        max_length=1,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            print(f"🔍 [FEEDBACK] Модалка отправлена пользователем {interaction.user}")
        
            # Сохраняем в базу данных
            feedback = create_feedback(
                user_id=interaction.user.id,
                user_name=interaction.user.display_name,
                title=self.title_input.value,
                message=self.message_input.value,
                rating=int(self.rating_input.value)
            )
            print(f"🔍 [FEEDBACK] Отзыв сохранен с ID: {feedback.id}")
            print(f"🔍 [FEEDBACK MODAL] Создан отзыв с ID: {feedback.id}")
            print(f"🔍 [FEEDBACK MODAL] Создаем View с feedback_id: {feedback.id}")
        
            # Отправляем в канал модерации
            print(f"🔍 [FEEDBACK] Ищем канал модерации ID: {FEEDBACK_CHANNEL_ID}")
            mod_channel = self.bot.get_channel(FEEDBACK_CHANNEL_ID)
            print(f"🔍 [FEEDBACK] Найденный канал: {mod_channel}")
        
            if mod_channel:
                print(f"🔍 [FEEDBACK] Канал найден: {mod_channel.name}")
            
                from .views import FeedbackModerationView
                embed = discord.Embed(
                    title=f"📝 {feedback.title}",
                    description=feedback.message,
                    color=0xf39c12,
                    timestamp=datetime.now()
                )
                embed.add_field(name="⭐ Оценка", value="★" * feedback.rating + "☆" * (5 - feedback.rating), inline=True)
                embed.add_field(name="👤 Автор", value=f"{interaction.user.mention}", inline=True)
                embed.set_footer(text=f"ID: {feedback.id} • Ожидание модерации")
            
                view = FeedbackModerationView(feedback.id, self.bot)
                await mod_channel.send(embed=embed, view=view)
                print(f"🔍 [FEEDBACK] Сообщение отправлено в канал модерации")
            else:
                print(f"❌ [FEEDBACK] Канал не найден! ID: {FEEDBACK_CHANNEL_ID}")
                await interaction.response.send_message(
                    "❌ Канал модерации не настроен. Сообщите администратору.",
                    ephemeral=True
                )
                return
        
            # Обновляем закрепленное сообщение (создаем PinService внутри)
            try:
                from .pin_service import PinService
                pin_service = PinService(self.bot)
                await pin_service.create_or_update_pinned_message(interaction.channel)
                print(f"🔍 [FEEDBACK] Закрепленное сообщение обновлено")
            except Exception as e:
                print(f"⚠️ [FEEDBACK] Не удалось обновить закрепленное сообщение: {e}")
        
            await interaction.response.send_message(
                f"✅ Ваш отзыв **{self.title_input.value}** отправлен на модерацию!",
                ephemeral=True,
                delete_after=10
            )
        
        except Exception as e:
            print(f"❌ [FEEDBACK] Ошибка: {e}")
            import traceback
            traceback.print_exc()
        
            await interaction.response.send_message(
                "❌ Ошибка при отправке отзыва",
                ephemeral=True,
                delete_after=10
            )