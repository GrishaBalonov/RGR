import logging
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime

# Применяем nest_asyncio
nest_asyncio.apply()

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Хранилище для заявок
applications = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправьте мне вашу заявку.')

# Обработка заявок
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_text = update.message.text
    # Валидация ввода
    if not user_text.strip():
        await update.message.reply_text("Ошибка: Заявка не может быть пустой.")
        return
    # Сохраняем заявку с пометкой о статусе "принята"
    applications[user_id] = {
        "text": user_text,
        "status": "Принята",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    await update.message.reply_text(f'Ваша заявка "{user_text}" принята!')

# Команда для проверки статуса заявки
async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    application = applications.get(update.message.from_user.id, None)
    if application:
        status = application["status"]
        timestamp = application["timestamp"]
        await update.message.reply_text(f'Статус вашей заявки: {status}. Заявка: {application["text"]}. Дата подачи: {timestamp}.')
    else:
        await update.message.reply_text("У вас нет поданной заявки.")

# Команда для отмены заявки
async def cancel_application(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in applications:
        del applications[user_id]
        await update.message.reply_text("Ваша заявка была отменена.")
    else:
        await update.message.reply_text("У вас нет поданной заявки для отмены.")

# Команда для просмотра всех заявок
async def view_applications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_apps = [f'Заявка: "{app["text"]}", Статус: {app["status"]}, Дата подачи: {app["timestamp"]}'
                 for app in applications.values() if user_id in applications]
    if user_apps:
        await update.message.reply_text("\n".join(user_apps))
    else:
        await update.message.reply_text("У вас нет поданных заявок.")

# Функция для запуска бота
async def main() -> None:
    # Вставьте ваш токен API
    app = ApplicationBuilder().token("7510801027:AAFwjz0949fb_P1vIcB6NVbbJNjJeqQL_Sk").build()

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("status", check_status))
    app.add_handler(CommandHandler("cancel", cancel_application))
    app.add_handler(CommandHandler("view_apps", view_applications))

    # Запускаем бота
    await app.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if 'This event loop is already running' in str(e):
            logger.warning("Используйте существующий цикл событий.")
