import discord
from datetime import datetime
from database_reports.operations import update_report_status

class ReportModerationView(discord.ui.View):
    def __init__(self, report_id: int = 0, bot = None, target_user_id: int = 0, target_user_name: str = ""):
        super().__init__(timeout=None)
        print(f"🔍 [REPORT VIEW] Создан новый View")
        # Параметры игнорируются после перезапуска
    
    @discord.ui.button(label='Принять', style=discord.ButtonStyle.success, emoji='✅', custom_id='approve_report')
    async def approve_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"🔍 [REPORT MOD] Кнопка 'Принять' нажата")
        
        # ВОССТАНАВЛИВАЕМ ВСЕ ДАННЫЕ ИЗ СООБЩЕНИЯ
        try:
            original_embed = interaction.message.embeds[0]
            print(f"🔍 [REPORT MOD] Заголовок: {original_embed.title}")
            print(f"🔍 [REPORT MOD] Footer: {original_embed.footer.text}")
            print(f"🔍 [REPORT MOD] Поля: {[f.name + ': ' + f.value for f in original_embed.fields]}")
            
            # Получаем report_id из footer
            footer_text = original_embed.footer.text
            report_id = int(footer_text.split("ID: ")[1].split(" •")[0])
            print(f"🔍 [REPORT MOD] Найден ID: {report_id}")
            
            # Получаем target_user_id из поля "На кого"
            target_user_id = None
            for field in original_embed.fields:
                if "На кого" in field.name:
                    if "<@" in field.value:
                        target_user_id = int(field.value.split('<@')[1].split('>')[0])
                        break
            
            print(f"🔍 [REPORT MOD] Target user ID: {target_user_id}")
            
        except Exception as e:
            print(f"❌ [REPORT MOD] Не удалось получить данные из сообщения: {e}")
            await interaction.response.send_message('❌ Не удалось найти данные жалобы', ephemeral=True)
            return
        
        # Обновляем статус в базе
        report = update_report_status(report_id, 'approved', str(interaction.user.id))
        
        if report:
            print(f"✅ [REPORT MOD] Жалоба обновлена: {report.id}")
            
            # Обновляем Embed
            embed = discord.Embed(
                title="✅ Жалоба ПРИНЯТА",
                description=report.report_description,
                color=0x2ecc71,
                timestamp=datetime.now()
            )
            embed.add_field(name="👤 От кого", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="👤 На кого", value=f"<@{target_user_id}>", inline=True)
            embed.add_field(name="👨‍💼 Модератор", value=f"{interaction.user.mention}", inline=True)
            embed.set_footer(text=f"ID: {report.id} • Принято {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message('✅ Жалоба принята!', ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message('❌ Жалоба не найдена в базе!', ephemeral=True, delete_after=10)
    
    @discord.ui.button(label='Отклонить', style=discord.ButtonStyle.danger, emoji='❌', custom_id='reject_report')
    async def reject_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"🔍 [REPORT MOD] Кнопка 'Отклонить' нажата")
        
        # ВОССТАНАВЛИВАЕМ ВСЕ ДАННЫЕ ИЗ СООБЩЕНИЯ
        try:
            original_embed = interaction.message.embeds[0]
            print(f"🔍 [REPORT MOD] Заголовок: {original_embed.title}")
            print(f"🔍 [REPORT MOD] Footer: {original_embed.footer.text}")
            print(f"🔍 [REPORT MOD] Поля: {[f.name + ': ' + f.value for f in original_embed.fields]}")
            
            # Получаем report_id из footer
            footer_text = original_embed.footer.text
            report_id = int(footer_text.split("ID: ")[1].split(" •")[0])
            print(f"🔍 [REPORT MOD] Найден ID: {report_id}")
            
            # Получаем target_user_id из поля "На кого"
            target_user_id = None
            for field in original_embed.fields:
                if "На кого" in field.name:
                    if "<@" in field.value:
                        target_user_id = int(field.value.split('<@')[1].split('>')[0])
                        break
            
            print(f"🔍 [REPORT MOD] Target user ID: {target_user_id}")
            
        except Exception as e:
            print(f"❌ [REPORT MOD] Не удалось получить данные из сообщения: {e}")
            await interaction.response.send_message('❌ Не удалось найти данные жалобы', ephemeral=True)
            return
        
        # Обновляем статус в базе
        report = update_report_status(report_id, 'rejected', str(interaction.user.id))
        
        if report:
            print(f"✅ [REPORT MOD] Жалоба отклонена: {report.id}")
            
            # Обновляем Embed
            embed = discord.Embed(
                title="❌ Жалоба ОТКЛОНЕНА",
                description=report.report_description,
                color=0xe74c3c,
                timestamp=datetime.now()
            )
            embed.add_field(name="👤 От кого", value=f"{interaction.user.mention}", inline=True)
            embed.add_field(name="👤 На кого", value=f"<@{target_user_id}>", inline=True)
            embed.add_field(name="👨‍💼 Модератор", value=f"{interaction.user.mention}", inline=True)
            embed.set_footer(text=f"ID: {report.id} • Отклонено {datetime.now().strftime('%d.%m.%Y %H:%M')}")
            
            await interaction.message.edit(embed=embed, view=None)
            await interaction.response.send_message('❌ Жалоба отклонена!', ephemeral=True, delete_after=10)
        else:
            await interaction.response.send_message('❌ Жалоба не найдена в базе!', ephemeral=True, delete_after=10)