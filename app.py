import os
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '').strip()
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '').strip()

if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    logger.error("Environment variables not set properly")
    exit(1)

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

def start(update, context):
    user = update.effective_user
    update.message.reply_text(
        f"Hi {user.first_name}! I'm a ChatGPT-powered bot. "
        "Send me a message and I'll respond with AI-generated content."
    )

def help_command(update, context):
    help_text = """
    Available commands:
    /start - Start the bot
    /help - Show this help message
    
    Or simply send a message to chat with the AI directly.
    """
    update.message.reply_text(help_text)

def chat_with_gpt(prompt):
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
    user_message = update.message.text
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    response = chat_with_gpt(user_message)
    update.message.reply_text(response)

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
