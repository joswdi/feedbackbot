import discord
from discord import app_commands
from .modals import ReportModal
from database_reports.operations import get_report_stats, reset_all_reports

def setup_report_commands(bot):
    """Регистрация команд для системы жалоб"""

    # Основная команда для подачи жалобы
    @bot.tree.command(name="report_user", description="Подать жалобу")
    @app_commands.describe(
        user="Пользователь, на которого подается жалоба"
    )
    async def report_slash(interaction: discord.Interaction, user: discord.User):
        """Вызывает модальное окно для жалобы"""
        print(f"🔍 Команда /report_user вызвана на пользователя {user}")
        try:
            modal = ReportModal(target_user=user, bot=bot)
            await interaction.response.send_modal(modal)
            print(f"🔍 Модальное окно отправлено")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            await interaction.response.send_message(
                f"❌ Не удалось открыть форму. Жалоба на {user.mention}",
                ephemeral=True,
                delete_after=10
            )

    # Команды для админов/модераторов
    @bot.tree.command(name="report_stats", description="Показать статистику жалоб")
    async def report_stats_slash(interaction: discord.Interaction):
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
    
        stats = get_report_stats()
    
        embed = discord.Embed(title="📊 Статистика жалоб", color=0x9b59b6)
        embed.add_field(name="📈 Всего жалоб", value=stats['total'], inline=True)
        embed.add_field(name="⏳ Ожидают", value=stats['pending'], inline=True)
        embed.add_field(name="✅ Принято", value=stats['approved'], inline=True)
        embed.add_field(name="❌ Отклонено", value=stats['rejected'], inline=True)
    
        await interaction.response.send_message(embed=embed, ephemeral=False)

    @bot.tree.command(name='report_reset', description="Полностью очистить все жалобы из базы данных")
    async def report_reset_slash(interaction: discord.Interaction):
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
        
        try:
            deleted_count = reset_all_reports()
            await interaction.response.send_message(f'✅ Удалено {deleted_count} жалоб из базы данных!', ephemeral=True, delete_after=10)
        except Exception as e:
            await interaction.response.send_message(f'❌ Ошибка при очистке базы: {e}', ephemeral=True, delete_after=10)

    @bot.tree.command(name='report_list', description="Показать список всех жалоб")
    async def report_list_slash(interaction: discord.Interaction):
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
        
        from database_reports.operations import get_session
        from database_reports.models import Report
        
        session = get_session()
        reports = session.query(Report).all()
        
        if not reports:
            await interaction.response.send_message("📭 Жалоб нет", ephemeral=True)
            session.close()
            return
        
        embed = discord.Embed(title="📋 Все жалобы", color=0x3498db)
        
        for report in reports:
            status_emoji = "⏳" if report.status == "pending" else "✅" if report.status == "approved" else "❌"
            status_text = "Ожидает" if report.status == "pending" else "Принята" if report.status == "approved" else "Отклонена"
            
            embed.add_field(
                name=f"{status_emoji} Жалоба #{report.id}",
                value=(
                    f"**От:** {report.user_name}\n"
                    f"**На:** {report.target_user_name}\n"
                    f"**Статус:** {status_text}\n"
                    f"**Дата:** {report.created_at.strftime('%d.%m.%Y %H:%M')}"
                ),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=False)
        session.close()

    @bot.tree.command(name='report_help', description="Показать справку по командам жалоб")
    async def report_help_slash(interaction: discord.Interaction):
        allowed_role_ids = [1436746949582786581, 1436748986265374873, 1436746590911074520, 1436748150688714905, 1436747956186386542]
        user_role_ids = [role.id for role in interaction.user.roles]
        has_allowed_role = any(role_id in user_role_ids for role_id in allowed_role_ids)
    
        if not has_allowed_role:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🛡️ Команды системы жалоб",
            description="Список команд для управления жалобами",
            color=0xe74c3c
        )
        
        embed.add_field(
            name="👤 Для всех",
            value="`/report_user` - Подать жалобу на пользователя",
            inline=False
        )
        
        embed.add_field(
            name="📊 Статистика (модераторы)",
            value=(
                "`/report_stats` - Показать статистику жалоб\n"
                "`/report_list` - Показать список всех жалоб"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Управление (модераторы)",
            value="`/report_reset` - Очистить ВСЕ жалобы из базы",
            inline=False
        )
        
        embed.add_field(
            name="📖 Справка", 
            value="`/report_help` - Показать это сообщение",
            inline=False
        )
        
        embed.set_footer(text="💡 Используйте /report_user @username чтобы подать жалобу")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)