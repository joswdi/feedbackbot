import discord
from discord.ext import commands
from config import BOT_TOKEN, COMMAND_PREFIX
from database_feedback.operations import init_db as init_feedback_db
from database_reports.operations import init_db as init_reports_db
from feedback.commands import setup_feedback_commands
from reports.commands import setup_report_commands

print("🚀 Инициализация бота...")

# Инициализация обеих баз данных
init_feedback_db()
init_reports_db()

# Настройка бота
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=COMMAND_PREFIX,
    intents=intents,
    help_command=None
)

@bot.event
async def setup_hook():
    """Синхронизация команд при запуске"""
    print("🔄 Начало синхронизации команд...")

    from feedback.views import FeedbackView, FeedbackModerationView
    from reports.views import ReportModerationView
    
    bot.add_view(FeedbackView(channel=None, pin_service=None))
    bot.add_view(FeedbackModerationView(feedback_id=0, bot=bot))
    bot.add_view(ReportModerationView(report_id=0, bot=bot, target_user_id=0, target_user_name=""))
    
    print("✅ Персистентные View зарегистрированы")
    
    try:
        # Проверяем какие команды зарегистрированы
        print(f"🔍 Зарегистрировано команд: {len(bot.tree.get_commands())}")
        for cmd in bot.tree.get_commands():
            print(f"   - {cmd.name}")
        
        # Синхронизация
        print("🔄 Синхронизация с Discord...")
        synced = await bot.tree.sync()
        print(f'✅ Синхронизировано {len(synced)} команд')
        
        for cmd in synced:
            print(f'   - /{cmd.name}')
            
    except Exception as e:
        print(f'❌ Ошибка синхронизации: {e}')
        import traceback
        traceback.print_exc()

# Регистрация команд
setup_feedback_commands(bot)
setup_report_commands(bot)

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} успешно запущен!')
    print('🔧 Бот готов к работе')

@bot.event 
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('❌ Команда не найдена', delete_after=5)

if __name__ == "__main__":
    print("🔧 Запуск бота...")
    try:
        bot.run(BOT_TOKEN)
    except Exception as e:
        print(f'❌ Ошибка: {e}')