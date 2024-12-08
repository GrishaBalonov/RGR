import logging
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Применяем nest_asyncio
nest_asyncio.apply()

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище для заявок (можно заменить на базу данных)
applications = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправьте мне вашу заявку.')

# Обработка заявок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text
    # Здесь следует добавить проверку и валидацию данных
    applications[update.message.from_user.id] = user_text  # Сохраняем заявку по user_id
    await update.message.reply_text(f'Ваша заявка "{user_text}" принята!')

# Команда для просмотра статуса заявки
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = applications.get(update.message.from_user.id, "У вас нет поданной заявки.")
    await update.message.reply_text(f'Статус вашей заявки: {status}')

# Команда для просмотра всех заявок (для администраторов)
async def view_applications(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_apps = "\n".join(applications.values())
    await update.message.reply_text(f'Все заявки:\n{all_apps}')

# Функция для запуска бота
async def main() -> None:
    # Вставьте ваш токен API
    app = ApplicationBuilder().token("7510801027:AAFwjz0949fb_P1vIcB6NVbbJNjJeqQL_Sk").build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("status", check_status))
    app.add_handler(CommandHandler("view_apps", view_applications))  # Для администраторов

    # Запускаем бота
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if 'This event loop is already running' in str(e):
            logger.warning("Используйте существующий цикл событий.")