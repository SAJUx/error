import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, request
import openai

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
RENDER_URL = os.environ.get('RENDER_EXTERNAL_URL')

# Clean up API key
if OPENAI_API_KEY:
    OPENAI_API_KEY = OPENAI_API_KEY.strip()
    OPENAI_API_KEY = ''.join(char for char in OPENAI_API_KEY if char.isprintable())

# Validate API keys
if not TELEGRAM_BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set!")
    exit(1)

if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY not set!")
    exit(1)

if not OPENAI_API_KEY.startswith('sk-'):
    logger.error("OPENAI_API_KEY doesn't look valid! It should start with 'sk-'")
    exit(1)

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Flask app
app = Flask(__name__)

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
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
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

# Set up webhook
async def set_webhook():
    if RENDER_URL:
        await application.bot.set_webhook(url=f"{RENDER_URL}/telegram-webhook")
        logger.info("Webhook set successfully")
    else:
        logger.error("RENDER_EXTERNAL_URL not set!")

# Flask route for webhook
@app.route('/telegram-webhook', methods=['POST'])
async def webhook():
    """Receive updates from Telegram via webhook"""
    update = Update.de_json(await request.get_json(), application.bot)
    await application.process_update(update)
    return 'OK'

@app.route('/')
def home():
    return 'Telegram ChatGPT Bot is running!'

if __name__ == '__main__':
    # Initialize webhook when starting
    import asyncio
    asyncio.run(set_webhook())
    
    # Start Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
