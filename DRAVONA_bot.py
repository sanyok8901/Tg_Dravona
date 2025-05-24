import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# --- Настройки ---
TOKEN = "7528920511:AAE24_C0VclbZNqd-omTEbqLK1maGmBmBQQ"
ADMINS = [1763797493, 6695638905]
CHANNEL_USERNAME = "@dravonstar"  # Юзернейм канала для проверки

# --- Состояния для ConversationHandler ---
WAIT_SUPPORT_USERNAME = 1

# --- Коды ---
codes = {
    "fix": {"max_uses": 0, "used_by": set()},
    "fix1": {"max_uses": 0, "used_by": set()},
    "fix2": {"max_uses": 0, "used_by": set()},
    "fix3": {"max_uses": 0, "used_by": set()},
    "fix4": {"max_uses": 0, "used_by": set()},
    "fix5": {"max_uses": 0, "used_by": set()},
    "fix6": {"max_uses": 0, "used_by": set()},
    "fix7": {"max_uses": 0, "used_by": set()},
    "Bdek": {"max_uses": 2, "used_by": set()},
    "Sky": {"max_uses": 2, "used_by": set()},
    "Sold": {"max_uses": 3, "used_by": set()},
    "Ked": {"max_uses": 3, "used_by": set()},
    "Apw": {"max_uses": 5, "used_by": set()},
    "Okey": {"max_uses": 1, "used_by": set()},
    "Sisisi": {"max_uses": 1, "used_by": set()},
    "Barah": {"max_uses": 1, "used_by": set()},
    "Kizr": {"max_uses": 1, "used_by": set()},
    "Arka": {"max_uses": 1, "used_by": set()},
    "Dramo": {"max_uses": 1, "used_by": set()},
    "Ccel": {"max_uses": 1, "used_by": set()},

}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Проверка подписки ---
async def check_subscription(user_id, bot):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# --- Декоратор для проверки подписки ---
def require_subscription(handler_func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if not await check_subscription(user_id, context.bot):
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("Подписаться на канал", url="https://t.me/dravonstar")],
                [InlineKeyboardButton("Проверить подписку", callback_data="check_subscribe")]
            ])
            await update.effective_message.reply_text(
                "❗ Для использования бота нужно быть подписанным на канал @dravonstar.",
                reply_markup=keyboard
            )
            return ConversationHandler.END
        return await handler_func(update, context, *args, **kwargs)
    return wrapper

# --- Команда /start ---
@require_subscription
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [
            InlineKeyboardButton("Ввести код", callback_data="enter_code"),
            InlineKeyboardButton("Тех.поддержка", callback_data="support"),
            InlineKeyboardButton("🚀 Мини-апки", web_app=WebAppInfo(url="https://sanyok8901.github.io/dravona/")),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:", reply_markup=reply_markup
    )

# --- Обработка текста сообщений ---
@require_subscription
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # --- Обработка после inline-кнопок ---
    inline_state = context.user_data.get("inline_state")
    if inline_state == "WAIT_CODE":
        user_code = text.strip()
        user_id = update.message.from_user.id
        if user_code not in codes:
            await update.message.reply_text("❌ Код не найден. Попробуйте снова:")
            return
        code_info = codes[user_code]
        if user_id in code_info["used_by"]:
            await update.message.reply_text("❗Вы уже активировали этот код ранее.")
            context.user_data["inline_state"] = None
            return
        if code_info["max_uses"] != 0 and len(code_info["used_by"]) >= code_info["max_uses"]:
            await update.message.reply_text("⚠️ Этот код уже использован максимальным числом пользователей.")
            context.user_data["inline_state"] = None
            return
        context.user_data["code"] = user_code
        await update.message.reply_text("Теперь отправьте свой username (например: @username):")
        context.user_data["inline_state"] = "WAIT_USERNAME"
        return
    elif inline_state == "WAIT_USERNAME":
        user = update.message.from_user
        user_id = user.id
        username_input = text.strip()
        user_code = context.user_data.get("code")
        if not user_code or user_code not in codes:
            await update.message.reply_text("Ошибка. Попробуйте заново /start")
            context.user_data["inline_state"] = None
            return
        code_info = codes[user_code]
        if user_id in code_info["used_by"]:
            await update.message.reply_text("❗Вы уже активировали этот код ранее.")
            context.user_data["inline_state"] = None
            return
        if code_info["max_uses"] != 0 and len(code_info["used_by"]) >= code_info["max_uses"]:
            await update.message.reply_text("⚠️ Код уже активирован максимальным числом пользователей.")
            context.user_data["inline_state"] = None
            return
        code_info["used_by"].add(user_id)
        full_name = f"{user.first_name} {user.last_name or ''}".strip()
        real_username = f"@{user.username}" if user.username else "нет username"
        message = (
            f"📥 Новый пользователь активировал код!\n\n"
            f"👤 Имя: {full_name}\n"
            f"🆔 Telegram ID: {user.id}\n"
            f"🔗 Username из чата: {username_input}\n"
            f"🔗 Username из Telegram: {real_username}\n"
            f"🔐 Код: {user_code}\n"
            f"📊 Осталось активаций: "
            f"{code_info['max_uses'] - len(code_info['used_by']) if code_info['max_uses'] != 0 else '∞'}"
        )
        for admin_id in ADMINS:
            await context.bot.send_message(chat_id=admin_id, text=message)
        await update.message.reply_text("✅ Спасибо! Вы успешно активировали код.")
        context.user_data["inline_state"] = None
        return
    elif inline_state == "WAIT_SUPPORT_USERNAME":
        user = update.message.from_user
        username_sent = text.strip()
        real_username = f"@{user.username}" if user.username else "нет username"
        msg = (
            f"📩 Обращение в тех.поддержку!\n\n"
            f"👤 Имя: {user.first_name} {user.last_name or ''}\n"
            f"🆔 Telegram ID: {user.id}\n"
            f"🔗 Username из чата: {username_sent}\n"
            f"🔗 Username из Telegram: {real_username}"
        )
        for admin_id in ADMINS:
            await context.bot.send_message(chat_id=admin_id, text=msg)
        await update.message.reply_text("✅ Спасибо! Мы скоро с вами свяжемся.")
        context.user_data["inline_state"] = None
        return

    # --- Обычная логика ---
    if text == "Ввести код":
        await update.message.reply_text(
            "Введите код:", reply_markup=ReplyKeyboardRemove()
        )
        return "WAIT_CODE"

    elif text == "Тех.поддержка":
        await update.message.reply_text(
            "Пожалуйста, отправьте свой username (например: @yourname):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return WAIT_SUPPORT_USERNAME
    else:
        await update.message.reply_text("Неизвестная команда. Попробуйте ещё раз.")

# --- Callback для inline кнопок ---
async def inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "check_subscribe":
        user_id = query.from_user.id
        if await check_subscription(user_id, context.bot):
            await query.answer("✅ Подписка подтверждена!", show_alert=True)
            # После подтверждения подписки вызываем start через message, чтобы меню появилось
            if query.message:
                fake_update = Update(
                    update.update_id,
                    message=query.message
                )
                await start(fake_update, context)
        else:
            await query.answer("❗ Вы не подписаны на канал.", show_alert=True)
    elif query.data == "enter_code":
        await query.answer()
        await query.message.reply_text("Введите код:")
        context.user_data["inline_state"] = "WAIT_CODE"
    elif query.data == "support":
        await query.answer()
        await query.message.reply_text("Пожалуйста, отправьте свой username (например: @yourname):")
        context.user_data["inline_state"] = "WAIT_SUPPORT_USERNAME"
    else:
        await query.answer()

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            "WAIT_CODE": [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            "WAIT_USERNAME": [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
            WAIT_SUPPORT_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(inline_callback))
    application.run_polling()

    print("Бот запущен...")

if __name__ == "__main__":
    main()
