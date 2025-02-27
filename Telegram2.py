import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from keep_alive import keep_alive  # Import keep-alive function

# Placeholder bot token
TOKEN = "7744323494:AAHv5DP9E-IJBP8rKu_Y27vSyU30MuDa83o"
bot = telebot.TeleBot(TOKEN, parse_mode="MarkdownV2")

# Dictionary to store user messages
user_messages = {}

# Function to escape MarkdownV2 special characters
def escape_markdown(text):
    special_chars = r'\_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', text)

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    text = "👋 Welcome\\! Use /new to create a custom message with buttons\\."
    bot.send_message(message.chat.id, text)

# Create a new message
@bot.message_handler(commands=['new'])
def new_message(message):
    user_messages[message.chat.id] = {"text": "", "buttons": []}
    bot.send_message(message.chat.id, "📝 Send me the *message text* first\\.")

# Set message text
@bot.message_handler(func=lambda message: message.chat.id in user_messages and user_messages[message.chat.id]["text"] == "")
def set_message_text(message):
    user_messages[message.chat.id]["text"] = message.text
    bot.send_message(message.chat.id, "🔘 Now send me a *button label and URL* in this format:\n`Label | https://example.com`\n\nType /done when finished\\.", parse_mode="MarkdownV2")

# Add buttons
@bot.message_handler(func=lambda message: message.chat.id in user_messages and user_messages[message.chat.id]["text"] != "")
def add_button(message):
    if message.text == "/done":
        send_final_message(message.chat.id)
        return

    # Split label and URL
    parts = message.text.split("|")
    if len(parts) == 2:
        label = parts[0].strip()
        url = parts[1].strip()
        user_messages[message.chat.id]["buttons"].append((label, url))
        bot.send_message(message.chat.id, f"✅ Added button: [{escape_markdown(label)}]({escape_markdown(url)})\nSend another button or type /done\\.", parse_mode="MarkdownV2")
    else:
        bot.send_message(message.chat.id, "⚠️ Invalid format\\! Use: `Label | https://example.com`", parse_mode="MarkdownV2")

# Send final message with buttons
def send_final_message(chat_id):
    data = user_messages.get(chat_id)
    if not data:
        bot.send_message(chat_id, "❌ Error: No message found\\.")
        return

    markup = InlineKeyboardMarkup()
    for text, url in data["buttons"]:
        markup.add(InlineKeyboardButton(text, url=url))

    bot.send_message(chat_id, escape_markdown(data["text"]), reply_markup=markup, parse_mode="MarkdownV2")
    bot.send_message(chat_id, "✅ Message sent\\! Use /new to create another\\.")

# Keep the bot alive
keep_alive()

# Run the bot
bot.polling()
