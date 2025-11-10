import discord
from .views import FeedbackView

class PinService:
    def __init__(self, bot):
        self.bot = bot
        self.pinned_message_id = None

    async def create_or_update_pinned_message(self, channel):
        """Создает или обновляет закрепленное сообщение с кнопкой отзыва"""
        try:
            pins = await channel.pins()
            
            for pin in pins:
                if pin.author == self.bot.user:
                    if pin.components and any(hasattr(btn, 'label') and btn.label == 'Оставить отзыв' for btn in pin.components[0].children):
                        await pin.unpin()
                        await pin.delete()
                        print(f"🗑️ Удалено старое закрепленное сообщение: {pin.id}")
        except Exception as e:
            print(f"⚠️ Ошибка при очистке старых сообщений: {e}")
        
        embed = discord.Embed(
            title="💬 Система отзывов",
            description="Нам важно ваше мнение! Поделитесь своими впечатлениями о нашем сервере.",
            color=0x3498db
        )
        embed.add_field(
            name="🎯 Как оставить отзыв?",
            value="• Нажмите кнопку **'Оставить отзыв'** ниже\n• Заполните простую форму\n• Отправьте на модерацию",
            inline=False
        )
        embed.add_field(
            name="📋 Что происходит дальше?",
            value="• Ваш отзыв проверяется модерацией\n• После одобрения публикуется в общем канале\n• Мы учитываем все ваши предложения!",
            inline=False
        )
        embed.set_footer(text="💝 Спасибо за вашу обратную связь!")
        
        view = FeedbackView(channel, self)
        new_message = await channel.send(embed=embed, view=view)
        
        await new_message.pin()
        
        try:
            async for message in channel.history(limit=5):
                if message.type == discord.MessageType.pins_add:
                    await message.delete()
                    break
        except:
            pass
        
        self.pinned_message_id = new_message.id
        print(f"📌 Создано новое закрепленное сообщение: {new_message.id}")
        
        return new_message