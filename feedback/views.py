import discord
from datetime import datetime
from database.operations import update_feedback_status, delete_feedback, get_feedback_by_id
from config import APPROVED_CHANNEL_ID
from .modals import FeedbackModal

class FeedbackView(discord.ui.View):
    def __init__(self, channel, pin_service):
        super().__init__(timeout=None)
        self.channel = channel
        self.pin_service = pin_service
    
    @discord.ui.button(label='Оставить отзыв', style=discord.ButtonStyle.primary, emoji='📝', custom_id='leave_feedback')
    async def leave_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = FeedbackModal(self.channel, self.pin_service, interaction.client)
        await interaction.response.send_modal(modal)

class FeedbackModerationView(discord.ui.View):
    def __init__(self, feedback_id: int, original_channel, bot):
        super().__init__(timeout=None)
        self.feedback_id = feedback_id
        self.original_channel = original_channel
        self.bot = bot
    
    @discord.ui.button(label='Принять', style=discord.ButtonStyle.success, emoji='✅', custom_id='approve_feedback')
    async def approve_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Обновляем статус в базе
        feedback = update_feedback_status(self.feedback_id, 'approved', str(interaction.user.id))
        
        if feedback:
            # Обновляем сообщение в канале модерации
            embed = discord.Embed(
                title=f"📝 {feedback.title}",
                description=feedback.message,
                color=0x2ecc71,
                timestamp=datetime.now()
            )
            embed.add_field(name="⭐ Оценка", value="★" * feedback.rating + "☆" * (5 - feedback.rating), inline=True)
            embed.add_field(name="📊 Статус", value="✅ Принято", inline=True)
            embed.add_field(name="👤 Автор", value=f"<@{feedback.user_id}>`", inline=True)
            embed.add_field(name="👨‍💼 Принял", value=f"<@{interaction.user.id}>`", inline=True)
            embed.set_footer(text=f"ID: {feedback.id} • Принято {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            await interaction.message.edit(embed=embed, view=None)
            
            # Отправляем в канал принятых отзывов
            approved_channel = self.bot.get_channel(APPROVED_CHANNEL_ID)
            if approved_channel:
                approved_embed = discord.Embed(
                    title="🎉 Новый отзыв!",
                    description=feedback.message,
                    color=0x2ecc71,
                    timestamp=datetime.now()
                )
                approved_embed.add_field(name="⭐ Оценка", value="★" * feedback.rating + "☆" * (5 - feedback.rating), inline=True)
                approved_embed.add_field(name="👤 Автор", value=f"<@{feedback.user_id}>", inline=True)
                
                await approved_channel.send(embed=approved_embed)
            
            # Обновляем закрепленное сообщение
            from .pin_service import PinService
            pin_service = PinService(self.bot)
            await pin_service.create_or_update_pinned_message(self.original_channel)
            
            await interaction.response.send_message('✅ Отзыв принят! Закрепленное сообщение обновлено.', ephemeral=True)
    
    @discord.ui.button(label='Отклонить', style=discord.ButtonStyle.danger, emoji='❌', custom_id='reject_feedback')
    async def reject_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Обновляем статус в базе (чтобы отображался в статистике отклоненных)
        feedback = update_feedback_status(self.feedback_id, 'rejected', str(interaction.user.id))
        
        if feedback:
            # Обновляем сообщение
            embed = discord.Embed(
                title=f"📝 {feedback.title}",
                description=feedback.message,
                color=0xe74c3c,
                timestamp=datetime.now()
            )
            embed.add_field(name="⭐ Оценка", value="★" * feedback.rating + "☆" * (5 - feedback.rating), inline=True)
            embed.add_field(name="📊 Статус", value="❌ Отклонено", inline=True)
            embed.add_field(name="👨‍💼 Отклонил", value=f"@{interaction.user.id}`)", inline=True)
            embed.set_footer(text=f"ID: {feedback.id}")
            
            await interaction.message.edit(embed=embed, view=None)
            
            # Обновляем закрепленное сообщение
            from .pin_service import PinService
            pin_service = PinService(self.bot)
            await pin_service.create_or_update_pinned_message(self.original_channel)
            
            await interaction.response.send_message('❌ Отзыв отклонен! Закрепленное сообщение обновлено.', ephemeral=True)