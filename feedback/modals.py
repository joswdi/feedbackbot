import discord
from datetime import datetime
from database.operations import create_feedback
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
            rating = int(self.rating_input.value)
            if rating < 1 or rating > 5:
                await interaction.response.send_message('❌ Оценка должна быть от 1 до 5!', ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message('❌ Введите корректное число для оценки!', ephemeral=True)
            return
        
        # Сохраняем в базу данных
        feedback = create_feedback(
            user_id=str(interaction.user.id),
            user_name=interaction.user.display_name,
            title=self.title_input.value,
            message=self.message_input.value,
            rating=rating
        )
        
        # Отправляем в канал модерации
        mod_channel = self.bot.get_channel(FEEDBACK_CHANNEL_ID)
        if mod_channel:
            from .views import FeedbackModerationView
            
            embed = discord.Embed(
                title=f"📝 {self.title_input.value}",
                description=self.message_input.value,
                color=0xf39c12,
                timestamp=datetime.now()
            )
            embed.add_field(name="⭐ Оценка", value="★" * rating + "☆" * (5 - rating), inline=True)
            embed.add_field(name="📊 Статус", value="⏳ Ожидание", inline=True)
            embed.add_field(name="👤 Автор", value=f"{interaction.user.display_name}\n(`{interaction.user.id}`)", inline=True)
            embed.set_footer(text=f"ID: {feedback.id} • Ожидание модерации")
            
            view = FeedbackModerationView(feedback.id, self.channel, self.bot)
            await mod_channel.send(embed=embed, view=view)
            
            # Обновляем закрепленное сообщение
            await self.pin_service.create_or_update_pinned_message(self.channel)
            
            await interaction.response.send_message(
                '✅ Ваш отзыв отправлен на модерацию! Закрепленное сообщение обновлено.', 
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                '❌ Ошибка при отправке отзыва. Канал модерации не найден.', 
                ephemeral=True
            )