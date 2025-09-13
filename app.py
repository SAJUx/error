import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
from flask import Flask, request

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration - Set these as environment variables on Render
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()

# Validate environment variables
if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    logger.error("Environment variables not set properly")
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
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')}/webhook"
    try:
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return False

# Flask route for webhook
@app.route('/webhook', methods=['POST'])
async def webhook():
    """Receive updates from Telegram via webhook"""
    try:
        data = request.get_json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return 'OK'
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return 'Error', 500

@app.route('/')
def home():
    return 'Telegram ChatGPT Bot is running! Visit /setwebhook to setup webhook'

@app.route('/setwebhook')
async def set_webhook_route():
    success = await set_webhook()
    if success:
        return 'Webhook set successfully!'
    else:
        return 'Error setting webhook!', 500

if __name__ == '__main__':
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
