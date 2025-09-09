print("Full Advanced Bot (Multi-turn + Inline Buttons")

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from openai import OpenAI

# ==================== CONFIG ====================
OPENAI_API_KEY = "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"  # তোমার OpenAI API key
TELEGRAM_BOT_TOKEN = "7430202804:AAEOD7FV9gPHfO6shD8QrnL1vliR5Tv_ZKw"  # Telegram Bot token
# ==============================================

# OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# User tracking set & conversation history
users = set()
conversation_history = {}  # key = chat_id, value = list of messages

# ============ INLINE BUTTONS =============
def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton("/version", callback_data="version"),
         InlineKeyboardButton("/users", callback_data="users")],
        [InlineKeyboardButton("/photo", callback_data="photo")]
    ]
    return InlineKeyboardMarkup(keyboard)

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    await update.message.reply_text(
        "👋 হ্যালো! আমি Advanced GPT Telegram Group Bot।\n\n"
        "গ্রুপে যেকোনো মেসেজ পাঠালে আমি উত্তর দিবো।\n\n"
        "Supported commands:\n"
        "/version - GPT মডেল চেক করো\n"
        "/photo <prompt> [size] - ছবি জেনারেট করো\n"
        "/users - বট কতজন ব্যবহার করছে দেখাও\n\n"
        "Supported image sizes: 1024x1024, 1024x1536, 1536x1024, auto\n",
        reply_markup=get_main_keyboard()
    )

# /version command
async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        models = client.models.list()
        model_list = [m.id for m in models.data]
        await update.message.reply_text(f"✅ Available Models:\n{', '.join(model_list)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error fetching models: {e}")

# /photo command
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)
    if len(context.args) == 0:
        await update.message.reply_text("❌ Please provide a prompt. Example: /photo a futuristic city auto")
        return

    # last argument might be size
    if context.args[-1] in ["1024x1024", "1024x1536", "1536x1024", "auto"]:
        size = context.args[-1]
        prompt = " ".join(context.args[:-1])
    else:
        size = "1024x1024"  # default
        prompt = " ".join(context.args)

    try:
        resp = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size=size
        )
        image_url = resp.data[0].url
        await update.message.reply_text(image_url)
    except Exception as e:
        await update.message.reply_text(f"❌ Error generating image: {e}")

# /users command
async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"👥 Bot ব্যবহার করছে মোট {len(users)} জন user.")

# Callback Query (inline button)
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "version":
        await version(update, context)
    elif data == "users":
        await show_users(update, context)
    elif data == "photo":
        await query.message.reply_text("Use /photo <prompt> [size] command to generate image.")

# Group Chat Handler with multi-turn
async def group_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_user.id)

    if update.effective_chat.type not in ["group", "supergroup"]:
        return

    chat_id = update.effective_chat.id
    user_text = update.message.text
    if not user_text:
        return

    # Conversation history tracking
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    conversation_history[chat_id].append({"role": "user", "content": user_text})

    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=conversation_history[chat_id]
        )
        answer = resp.output_text
        await update.message.reply_text(answer)

        # Save GPT reply to conversation
        conversation_history[chat_id].append({"role": "assistant", "content": answer})

    except Exception as e:
        await update.message.reply_text(f"❌ GPT Error: {e}")

# ==================== MAIN ====================
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("version", version))
    app.add_handler(CommandHandler("photo", photo))
    app.add_handler(CommandHandler("users", show_users))

    # Inline buttons
    app.add_handler(CallbackQueryHandler(button))

    # Group auto-reply handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, group_chat))

    print("✅ Advanced Group GPT Bot চলছে...")
    app.run_polling()

if __name__ == "__main__":
    main()


