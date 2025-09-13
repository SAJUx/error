import os
import logging
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
from flask import Flask, request

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

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram Bot with older version compatible code
bot = Bot(token=TELEGRAM_BOT_TOKEN)
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_text(
        f"Hi {user.first_name}! I'm a ChatGPT-powered bot. "
        "Send me a message and I'll respond with AI-generated content."
    )

def help_command(update, context):
    """Send a message when the command /help is issued."""
    help_text = """
    Available commands:
    /start - Start the bot
    /help - Show this help message
    
    Or simply send a message to chat with the AI directly.
    """
    update.message.reply_text(help_text)

def chat_with_gpt(prompt):
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

def handle_message(update, context):
    """Handle incoming messages and respond using ChatGPT."""
    user_message = update.message.text
    
    # Show typing action while processing
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Get response from ChatGPT
    response = chat_with_gpt(user_message)
    
    # Send the response
    update.message.reply_text(response)

# Add handlers
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Set up webhook
def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')}/webhook"
    try:
        bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to: {webhook_url}")
        return True
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return False

# Flask route for webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive updates from Telegram via webhook"""
    try:
        data = request.get_json()
        update = Update.de_json(data, bot)
        dispatcher.process_update(update)
        return 'OK'
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return 'Error', 500

@app.route('/')
def home():
    return 'Telegram ChatGPT Bot is running! Visit /setwebhook to setup webhook'

@app.route('/setwebhook')
def set_webhook_route():
    success = set_webhook()
    if success:
        return 'Webhook set successfully!'
    else:
        return 'Error setting webhook!', 500

if __name__ == '__main__':
    # Start Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
