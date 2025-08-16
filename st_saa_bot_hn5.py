import random
import os
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Укажите токен вашего бота, его можно получить у @BotFather
BOT_TOKEN = "1111111111:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"

# ID вашего приватного канала
PRIVATE_CHANNEL_ID = "@канал где бот админ"

# Путь к текстовому файлу, ОН ДОЛЖЕН БЫТЬ ВОЗЛЕ ФАЙЛА БОТА, ну или хотя бы в той же директории
file_path = os.path.join(os.path.dirname(__file__), "SaA_memory.txt") # Заменить название на свое

# Список для хранения message_id медиафайлов
media_message_ids = []

# Функция для чтения message_id из файла
def load_media_message_ids():
    global media_message_ids
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            media_message_ids = [int(line.strip()) for line in f.readlines()]
    else:
        media_message_ids = []

# Функция для сохранения message_id в файл
def save_media_message_id(message_id):
    with open(file_path, 'a') as f:
        f.write(f"{message_id}\n")

# Обработчик команды /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("Рандомный хент")],
        [KeyboardButton("Загрузить свой")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привет! Я бот от компании SaA™. Используйте кнопки ниже, чтобы взаимодействовать.",
        reply_markup=reply_markup
    )

# Обработчик команды "Загрузить"
async def upload_command(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Пожалуйста, отправьте мне изображение или видео. Но помните! Не более 10 файлов за раз с перерывом в 15 секунд.")

# Обработчик загрузки файлов
async def handle_upload(update: Update, context: CallbackContext) -> None:
    global media_message_ids

    # Проверяем, что сообщение пришло из личного чата
    if update.message.chat.type == 'private':
        # Если загружено изображение
        if update.message.photo:
            file_id = update.message.photo[-1].file_id
            msg = await context.bot.send_photo(chat_id=PRIVATE_CHANNEL_ID, photo=file_id)
            media_message_ids.append(msg.message_id)
            save_media_message_id(msg.message_id)  # Сохранение в файл
            await update.message.reply_text("Ваше изображение загружено в библиотеку бота.")
        
        # Если загружено видео
        elif update.message.video:
            file_id = update.message.video.file_id
            msg = await context.bot.send_video(chat_id=PRIVATE_CHANNEL_ID, video=file_id)
            media_message_ids.append(msg.message_id)
            save_media_message_id(msg.message_id)  # Сохранение в файл
            await update.message.reply_text("Ваше видео загружено в библиотеку бота.")
        
        else:
            await update.message.reply_text("Пожалуйста, отправьте изображение или видео.")

# Обработчик команды для отправки рандомного котика
async def send_random_cat(update: Update, context: CallbackContext) -> None:
    global media_message_ids

    if media_message_ids:
        # Выбираем случайный message_id
        if random.random() < 0.6: # 60% "свежак"
            pool = media_message_ids[-50:] # последние 50 айди = "свежак"
        else:
            pool = media_message_ids
        random_message_id = random.choice(pool)
        
        # Пересылаем сообщение с медиафайлом из канала
        forwarded_message = await context.bot.forward_message(chat_id=update.message.chat_id, from_chat_id=PRIVATE_CHANNEL_ID, message_id=random_message_id)
        
        # Дублируем отправку медиафайла без пересылки
        if forwarded_message.photo:
            await context.bot.send_photo(chat_id=update.message.chat_id, photo=forwarded_message.photo[-1].file_id)
        elif forwarded_message.video:
            await context.bot.send_video(chat_id=update.message.chat_id, video=forwarded_message.video.file_id)
        
        # Удаляем пересланное сообщение
        await context.bot.delete_message(chat_id=update.message.chat_id, message_id=forwarded_message.message_id)
    else:
        await update.message.reply_text("Нет доступных медиафайлов в канале.")

# Обработчик текстовых сообщений
async def handle_text(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if text == "Рандомный хент":
        await send_random_cat(update, context)
    elif text == "Загрузить свой":
        await upload_command(update, context)

if __name__ == '__main__':

    # Загружаем существующие message_id из файла при старте
    load_media_message_ids()

    # Создание и запуск приложения Telegram
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавление обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND, handle_upload))
    application.add_handler(MessageHandler(filters.VIDEO & ~filters.COMMAND, handle_upload))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Запуск бота
    application.run_polling()
