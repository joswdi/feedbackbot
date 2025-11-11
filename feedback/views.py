import discord
from datetime import datetime
from database_feedback.operations import update_feedback_status
from config import APPROVED_CHANNEL_ID
from .modals import FeedbackModal

class FeedbackView(discord.ui.View):
    def __init__(self, channel, pin_service):
        super().__init__(timeout=None)
        self.channel = channel
        self.pin_service = pin_service
    
    @discord.ui.button(label='Оставить отзыв', style=discord.ButtonStyle.primary, emoji='📝', custom_id='leave_feedback')
    async def leave_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.response.is_done():
            return
            
        try:
            # Создаем PinService и используем interaction.channel
            from .pin_service import PinService
            pin_service = PinService(interaction.client)
            modal = FeedbackModal(interaction.channel, pin_service, interaction.client)
            await interaction.response.send_modal(modal)
        except Exception as e:
            print(f"❌ Ошибка при открытии модалки: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Не удалось открыть форму отзыва", 
                    ephemeral=True, 
                    delete_after=5
                )

class FeedbackModerationView(discord.ui.View):
    def __init__(self, feedback_id: int = 0, bot = None):
        super().__init__(timeout=None)
        # Эти параметры игнорируются после перезапуска
        # Восстанавливаем состояние из сообщения
    
    @discord.ui.button(label='Принять', style=discord.ButtonStyle.success, emoji='✅', custom_id='approve_feedback')
    async def approve_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"🔍 [FEEDBACK MOD] Кнопка 'Принять' нажата")
        
        # ВОССТАНАВЛИВАЕМ feedback_id из сообщения
        try:
            original_embed = interaction.message.embeds[0]
            footer_text = original_embed.footer.text
            feedback_id = int(footer_text.split("ID: ")[1].split(" •")[0])
            print(f"🔍 [FEEDBACK MOD] Получили ID из footer: {feedback_id}")
        except Exception as e:
            print(f"❌ [FEEDBACK MOD] Не удалось получить ID из сообщения: {e}")
            await interaction.response.send_message('❌ Не удалось найти ID отзыва', ephemeral=True)
            return
        
        # Обновляем статус в базе
        feedback = update_feedback_status(feedback_id, 'approved', str(interaction.user.id))
        
        if feedback:
            print(f"✅ [FEEDBACK MOD] Отзыв найден и обновлен: {feedback.id}")
            # Обновляем Embed
            embed = discord.Embed(
                title=f"📝 {feedback.title}",
                description=feedback.message,
                color=0x2ecc71,
                timestamp=datetime.now()
            )
            embed.add_field(name="⭐ Оценка", value="★" * feedback.rating + "☆" * (5 - feedback.rating), inline=True)
            embed.add_field(name="📊 Статус", value="✅ Принято", inline=True)
            embed.add_field(name="👤 Автор", value=f"<@{feedback.user_id}>", inline=True)
            embed.add_field(name="👨‍💼 Принял", value=f"{interaction.user.mention}", inline=True)
            embed.set_footer(text=f"ID: {feedback.id} • Принято {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            await interaction.message.edit(embed=embed, view=None)
            
            # Отправляем в канал принятых отзывов
            from config import APPROVED_CHANNEL_ID
            approved_channel = interaction.client.get_channel(APPROVED_CHANNEL_ID)
            if approved_channel:
                print(f"🔍 [FEEDBACK MOD] Отправляем в канал принятых: {APPROVED_CHANNEL_ID}")
                approved_embed = discord.Embed(
                    title="🎉 Новый отзыв!",
                    description=feedback.message,
                    color=0x2ecc71,
                    timestamp=datetime.now()
                )
                approved_embed.add_field(name="⭐ Оценка", value="★" * feedback.rating + "☆" * (5 - feedback.rating), inline=True)
                approved_embed.add_field(name="👤 Автор", value=f"<@{feedback.user_id}>", inline=True)
                
                await approved_channel.send(embed=approved_embed)
            
            await interaction.response.send_message('✅ Отзыв принят!', ephemeral=True, delete_after=5)
        else:
            print(f"❌ [FEEDBACK MOD] Отзыв с ID {feedback_id} не найден в базе!")
            await interaction.response.send_message('❌ Отзыв не найден в базе!', ephemeral=True, delete_after=5)
    
    @discord.ui.button(label='Отклонить', style=discord.ButtonStyle.danger, emoji='❌', custom_id='reject_feedback')
    async def reject_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"🔍 [FEEDBACK MOD] Кнопка 'Отклонить' нажата")
        
        # ВОССТАНАВЛИВАЕМ feedback_id из сообщения
        try:
            original_embed = interaction.message.embeds[0]
            footer_text = original_embed.footer.text
            feedback_id = int(footer_text.split("ID: ")[1].split(" •")[0])
            print(f"🔍 [FEEDBACK MOD] Получили ID из footer: {feedback_id}")
        except Exception as e:
            print(f"❌ [FEEDBACK MOD] Не удалось получить ID из сообщения: {e}")
            await interaction.response.send_message('❌ Не удалось найти ID отзыва', ephemeral=True)
            return
        
        # Обновляем статус в базе
        feedback = update_feedback_status(feedback_id, 'rejected', str(interaction.user.id))
        
        if feedback:
            print(f"✅ [FEEDBACK MOD] Отзыв найден и отклонен: {feedback.id}")
            # Обновляем Embed
            embed = discord.Embed(
                title=f"📝 {feedback.title}",
                description=feedback.message,
                color=0xe74c3c,
                timestamp=datetime.now()
            )
            embed.add_field(name="⭐ Оценка", value="★" * feedback.rating + "☆" * (5 - feedback.rating), inline=True)
            embed.add_field(name="📊 Статус", value="❌ Отклонено", inline=True)
            embed.add_field(name="👨‍💼 Отклонил", value=f"{interaction.user.mention}", inline=True)
            embed.set_footer(text=f"ID: {feedback.id} • Отклонено {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            await interaction.message.edit(embed=embed, view=None)
            
            await interaction.response.send_message('❌ Отзыв отклонен!', ephemeral=True, delete_after=5)
        else:
            await interaction.response.send_message('❌ Отзыв не найден!', ephemeral=True, delete_after=5)