import asyncio
import logging
import signal
import sys
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from openai import OpenAI
import os

# 🔹 Env থেকে key গুলো আনো
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 🔹 OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔹 Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# --- Commands ---
async def start(update, context):
    await update.message.reply_text("🤖 GPT Bot Online! /help লিখে দেখো কী করতে পারো।")

async def help_command(update, context):
    await update.message.reply_text("📌 Available commands:\n/start - বট চালু করো\n/help - সাহায্য\nচ্যাট করতে শুধু মেসেজ দাও।")

async def chat(update, context):
    try:
        user_text = update.message.text
        response = client.responses.create(
            model="gpt-4o-mini",
            input=user_text
        )
        await update.message.reply_text(response.output_text)
    except Exception as e:
        logger.error(f"OpenAI Error: {e}")
        await update.message.reply_text("❌ দুঃখিত, কিছু সমস্যা হয়েছে। পরে আবার চেষ্টা করো।")

# --- Main Function ---
def main():
    logger.info("🚀 Starting GPT Telegram Bot...")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    # Signal handling (CTRL+C, SIGTERM ইত্যাদি ধরতে পারবে)
    loop = asyncio.get_event_loop()

    def shutdown():
        logger.info("🛑 Shutdown signal received! Stopping bot...")
        loop.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    try:
        logger.info("✅ Bot is running... Press Ctrl+C to stop (Termux style).")
        app.run_polling()
    except Exception as e:
        logger.critical(f"🔥 Bot crashed: {e}", exc_info=True)
    finally:
        logger.info("👋 Bot stopped cleanly.")

# Run bot
if __name__ == "__main__":
    main()
