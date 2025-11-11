import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# ID каналов
FEEDBACK_CHANNEL_ID = int(os.getenv('FEEDBACK_CHANNEL_ID', '0'))
APPROVED_CHANNEL_ID = int(os.getenv('APPROVED_CHANNEL_ID', '0'))
REPORT_CHANNEL_ID = int(os.getenv('REPORT_CHANNEL_ID', '0'))

# Префикс команд
COMMAND_PREFIX = '/'

# База данных
DATABASE_FEEDBACK_URL = os.getenv('DATABASE_FEEDBACK_URL', 'sqlite:///feedback.db')
DATABASE_REPORTS_URL = os.getenv('DATABASE_REPORTS_URL', 'sqlite:///reports.db')

# Проверка обязательных переменных
if not BOT_TOKEN:
    print("❌ ОШИБКА: DISCORD_BOT_TOKEN не найден в .env файле!")
    exit(1)

print("✅ Конфигурация загружена успешно")