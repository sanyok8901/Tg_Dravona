import logging
from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    WebAppInfo,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# --- Настройки ---
TOKEN = "7528920511:AAE2ITtGYan0CmK7ySkNBYukEgMh92vEMjQ"
ADMINS = [1763797493, 6695638905]

# --- Состояния для ConversationHandler ---
WAIT_SUPPORT_USERNAME = 1

# --- Коды ---
codes = {
    "TESTCODE": {"max_uses": 1, "used_by": set()},
}

# --- Логирование ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# --- Команда /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [KeyboardButton("Ввести код")],
        [KeyboardButton("Информация"), KeyboardButton("Тех.поддержка")],
        [KeyboardButton("‼️🟨Бесплатная рулетка🟨‼️")],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    inline_buttons = [
        [
            InlineKeyboardButton(
                "Поддержать канал ⭐️", callback_data="support_channel"
            ),
            InlineKeyboardButton(
                "🚀 Мини-апки",
                web_app=WebAppInfo(url="https://sanyok8901.github.io/dravona/"),
            ),
        ]
    ]
    inline_markup = InlineKeyboardMarkup(inline_buttons)

    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:", reply_markup=reply_markup
    )
    await update.message.reply_text("Или используйте кнопки ниже:", reply_markup=inline_markup)


# --- Обработка текста сообщений ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Ввести код":
        await update.message.reply_text(
            "Введите код:", reply_markup=ReplyKeyboardRemove()
        )
        return "WAIT_CODE"

    elif text == "Информация":
        await update.message.reply_text(
            "📌 ИНФОРМАЦИЯ О НАШЕМ БОТЕ\n\n"
            "Мы открылись недавно, наш канал — @dravonstar\n\n"
            "Мы сообщаем интересные новости про подарки Telegram, а также сами их раздаём 🎁"
        )
    elif text == "‼️🟨Бесплатная рулетка🟨‼️":
        await update.message.reply_text(
            "🎰 Simple question\n\n"
            "❗️БЕСПЛАТНАЯ РУЛЕТКА, ГДЕ МОЖЕТ ВЫПАСТЬ ПОДАРОК, NFT ИЛИ ТОКЕНЫ ❗️\n\n"
            "Заходите в бота, потом в рулетку — и крутите бесплатно каждые 24 часа!\n"
            "Получайте прикольные призы и делитесь, что выпало 🧸💝\n\n"
            "@virus_play_bot"
        )
    elif text == "Тех.поддержка":
        await update.message.reply_text(
            "Пожалуйста, отправьте свой username (например: @yourname):",
            reply_markup=ReplyKeyboardRemove(),
        )
        return WAIT_SUPPORT_USERNAME
    else:
        await update.message.reply_text("Неизвестная команда. Попробуйте ещё раз.")


# --- Обработка кода (сохранение) ---
async def receive_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_code = update.message.text.strip()
    user_id = update.message.from_user.id

    if user_code not in codes:
        await update.message.reply_text("❌ Код не найден. Попробуйте снова:")
        return "WAIT_CODE"

    code_info = codes[user_code]

    if user_id in code_info["used_by"]:
        await update.message.reply_text("❗Вы уже активировали этот код ранее.")
        return ConversationHandler.END

    if code_info["max_uses"] != 0 and len(code_info["used_by"]) >= code_info["max_uses"]:
        await update.message.reply_text(
            "⚠️ Этот код уже использован максимальным числом пользователей."
        )
        return ConversationHandler.END

    context.user_data["code"] = user_code
    await update.message.reply_text(
        "Теперь отправьте свой username (например: @username):"
    )
    return "WAIT_USERNAME"


# --- Обработка username после кода ---
async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username_input = update.message.text.strip()

    user_code = context.user_data.get("code")
    if not user_code or user_code not in codes:
        await update.message.reply_text("Ошибка. Попробуйте заново /start")
        return ConversationHandler.END

    code_info = codes[user_code]

    if user_id in code_info["used_by"]:
        await update.message.reply_text("❗Вы уже активировали этот код ранее.")
        return ConversationHandler.END

    if code_info["max_uses"] != 0 and len(code_info["used_by"]) >= code_info["max_uses"]:
        await update.message.reply_text(
            "⚠️ Код уже активирован максимальным числом пользователей."
        )
        return ConversationHandler.END

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
    return ConversationHandler.END


# --- Обработка username для тех.поддержки ---
async def support_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    username_sent = update.message.text.strip()
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
    return ConversationHandler.END


# --- Callback для inline кнопок ---
async def inline_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "support_channel":
        # Отправляем кнопки для оплаты 10, 30, 50, 100 звёзд
        prices_options = [10, 30, 50, 100]
        buttons = [
            [
                InlineKeyboardButton(
                    f"Оплатить {price} ⭐️", callback_data=f"pay_{price}"
                )
            ]
            for price in prices_options
        ]
        keyboard = InlineKeyboardMarkup(buttons)
        await query.message.reply_text(
            "Выберите сумму поддержки (в звёздах):", reply_markup=keyboard
        )
    elif query.data.startswith("pay_"):
        amount = int(query.data.split("_")[1])
        prices = [LabeledPrice(label="Поддержка канала", amount=amount)]
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=f"Оплатить {amount} ⭐️", pay=True)]]
        )

        await query.message.reply_invoice(
            title="Поддержка канала",
            description=f"Оплата {amount} звёзд Telegram Stars",
            payload=f"support_{amount}_{query.from_user.id}",
            provider_token="",  # Для Telegram Stars — пустая строка
            currency="XTR",
            prices=prices,
            reply_markup=keyboard,
        )


# --- Обработка pre_checkout ---
async def pre_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


# --- Успешная оплата ---
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Спасибо за оплату! Вы поддержали канал ⭐️")


def main():
    application = Application.builder().token(TOKEN).build()

    # Основной ConversationHandler для ввода кода
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)],
        states={
            "WAIT_CODE": [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_code)],
            "WAIT_USERNAME": [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)],
            WAIT_SUPPORT_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_username)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    application.add_handler(CallbackQueryHandler(inline_callback))
    application.add_handler(PreCheckoutQueryHandler(pre_checkout))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    application.run_polling()

    print("Бот запущен...")
    app.run_polling()


if __name__ == "__main__":
    main()
