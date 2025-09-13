import os
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - Set these as environment variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()

# Validate environment variables
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    logger.error("Environment variables not set properly")
    exit(1)

# Initialize OpenAI client (new async API)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Initialize Telegram Application
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! I'm a ChatGPT-powered bot. "
        "Send me a message and I'll respond with AI-generated content."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = """
    Available commands:
    /start - Start the bot
    /help - Show this help message
    
    Or simply send a message to chat with the AI directly.
    """
    await update.message.reply_text(help_text)

async def chat_with_gpt(prompt):
    """Send prompt to ChatGPT API and return the response."""
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in ChatGPT API call: {e}")
        return "Sorry, I'm having trouble connecting to the AI service right now."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages and respond using ChatGPT."""
    user_message = update.message.text
    
    # Show typing action while processing
    await update.message.chat.send_action(action="typing")
    
    # Get response from ChatGPT
    response = await chat_with_gpt(user_message)
    
    # Send the response
    await update.message.reply_text(response)

# Add handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

async def main():
    """Start the bot."""
    # Start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("Bot is running and polling for messages...")
    
    # Keep the application running
    await asyncio.Event().wait()

if __name__ == '__main__':
    # Run the bot
    asyncio.run(main())
