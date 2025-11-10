import discord
from discord.ext import commands
from config import BOT_TOKEN, COMMAND_PREFIX
from database.operations import init_db
from feedback.commands import setup_feedback_commands

print("🚀 Инициализация бота...")

# Инициализация базы данных
init_db()

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
    
    try:
        # Синхронизация для всех серверов (глобально)
        synced = await bot.tree.sync()
        print(f'✅ Глобально синхронизировано {len(synced)} команд')
        
        for cmd in synced:
            print(f'   - /{cmd.name}')
            
    except Exception as e:
        print(f'❌ Ошибка синхронизации: {e}')

# Регистрация команд
setup_feedback_commands(bot)

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