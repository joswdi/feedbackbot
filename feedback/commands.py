import discord
from database_feedback.operations import get_feedback_stats, reset_all_feedbacks
from .pin_service import PinService

def setup_feedback_commands(bot):
    """Регистрация команд для системы отзывов"""

    @bot.tree.command(name="feedback_setup", description="Запустите систему сбора отзывов(в крайних случаях)")
    async def feedback_setup_slash(interaction: discord.Interaction):
        pin_service = PinService(bot)
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
    
        message = await pin_service.create_or_update_pinned_message(interaction.channel)
        await interaction.response.send_message(
            f'✅ Закрепленное сообщение для отзывов создано! (ID: {message.id})',
            ephemeral=True,
            delete_after=10
        )

    @bot.tree.command(name="feedback_stats", description="Показать статистику отзывов")
    async def feedback_stats_slash(interaction: discord.Interaction):
        stats = get_feedback_stats()
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
    
        embed = discord.Embed(title="📊 Статистика отзывов", color=0x9b59b6)
        embed.add_field(name="📈 Всего отзывов", value=stats['total'], inline=True)
        embed.add_field(name="⏳ Ожидают", value=stats['pending'], inline=True)
        embed.add_field(name="✅ Принято", value=stats['approved'], inline=True)
        embed.add_field(name="❌ Отклонено", value=stats['rejected'], inline=True)
    
        if stats['approved'] > 0:
            embed.add_field(name="⭐ Средняя оценка", value=f"{stats['avg_rating']:.1f}/5", inline=True)
    
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="feedback_update", description="Обновить закреплённое сообщение с отзывами")
    async def feedback_update_slash(interaction: discord.Interaction):
        pin_service = PinService(bot)
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
        
        await pin_service.create_or_update_pinned_message(interaction.channel)
        await interaction.response.send_message('✅ Закрепленное сообщение обновлено!', ephemeral=True, delete_after=10)
    
    @bot.tree.command(name="feedback_cleanup", description="Очистить старые закрепленные сообщения")
    async def feedback_cleanup_slash(interaction: discord.Interaction):
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
        
        try:
            pins = await interaction.channel.pins()
            deleted_count = 0
            
            for pin in pins:
                if pin.author == bot.user:
                    if pin.components and any(hasattr(btn, 'label') and btn.label == 'Оставить отзыв' for btn in pin.components[0].children):
                        await pin.unpin()
                        await pin.delete()
                        deleted_count += 1
            
            await interaction.response.send_message(f'✅ Удалено {deleted_count} старых закрепленных сообщений!', ephemeral=True, delete_after=10)
        except Exception as e:
            await interaction.response.send_message(f'❌ Ошибка при очистке: {e}', ephemeral=True, delete_after=10)

    @bot.tree.command(name='feedback_reset', description="Полностью очистить все отзывы из базы данных")
    async def feedback_reset_slash(interaction: discord.Interaction):
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
        
        try:
            deleted_count = reset_all_feedbacks()
            await interaction.response.send_message(f'✅ Удалено {deleted_count} отзывов из базы данных!', ephemeral=True, delete_after=10)
        except Exception as e:
            await interaction.response.send_message(f'❌ Ошибка при очистке базы: {e}', ephemeral=True, delete_after=10)

    @bot.tree.command(name='feedback_help', description="Показать список доступных команд")
    async def help_command_slash(interaction: discord.Interaction):
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📋 Доступные команды",
            description="Список всех команд бота",
            color=0x3498db
        )
        
        # Команды отзывов
        embed.add_field(
            name="💬 Команды отзывов",
            value=(
                "`/feedback_setup` - Создать закрепленное сообщение\n"
                "`/feedback_stats` - Статистика отзывов\n"
                "`/feedback_update` - Обновить закрепленное сообщение\n"
                "`/feedback_cleanup` - Очистить старые сообщения\n"
                "`/feedback_reset` - Очистить ВСЕ отзывы из базы"
            ),
            inline=False
        )
        
        # Общие команды
        embed.add_field(
            name="🔧 Общие команды",
            value="`/feedback_help` - Показать это сообщение",
            inline=False
        )
        
        embed.set_footer(text="💡 Нажмите кнопку 'Оставить отзыв' в закрепленном сообщении")
        
        await interaction.response.send_message(embed=embed)