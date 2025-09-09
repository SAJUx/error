import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from openai import OpenAI

# 🔹 Env variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not OPENAI_API_KEY or not TELEGRAM_BOT_TOKEN:
    raise ValueError("Missing environment variables!")

# 🔹 OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔹 Handlers
def start(update, context):
    update.message.reply_text("🤖 GPT Bot Online! /help লিখে দেখো কী করতে পারো।")

def help_command(update, context):
    update.message.reply_text("📌 Commands: /start, /help. Chat by sending any message.")

def chat(update, context):
    user_text = update.message.text
    try:
        response = client.responses.create(
            model="gpt-4o-mini",
            input=user_text
        )
        update.message.reply_text(response.output_text)
    except Exception as e:
        update.message.reply_text("❌ দুঃখিত, কিছু সমস্যা হয়েছে। পরে আবার চেষ্টা করো.")

# 🔹 Main
updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))

updater.start_polling()
updater.idle()
