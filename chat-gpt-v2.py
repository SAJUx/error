import logging
import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from openai import OpenAI

# Env keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Logging
logging.basicConfig(level=logging.INFO)

# Commands
async def start(update, context):
    await update.message.reply_text("🤖 GPT Bot Online!")

async def help_command(update, context):
    await update.message.reply_text("📌 Commands: /start, /help")

async def chat(update, context):
    user_text = update.message.text
    response = client.responses.create(model="gpt-4o-mini", input=user_text)
    await update.message.reply_text(response.output_text)

# Main
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
