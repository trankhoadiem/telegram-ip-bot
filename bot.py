import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import openai
import requests

# Thiết lập API Key
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Cấu hình Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Hàm xử lý lệnh /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Chào bạn, tôi là bot Telegram của Lê Tuấn Điềm. Để bắt đầu, bạn có thể sử dụng các lệnh sau:\n"
        "/help - Hướng dẫn sử dụng bot\n"
        "/gpt - Sử dụng ChatGPT\n"
        "/grok - Sử dụng Grok 3\n"
        "/gemini - Sử dụng Gemini\n"
    )

# Hàm xử lý lệnh /help
def help(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Các lệnh của bot:\n"
        "/gpt - Trò chuyện với ChatGPT\n"
        "/grok - Trò chuyện với Grok 3\n"
        "/gemini - Trò chuyện với Gemini\n"
    )

# Hàm xử lý lệnh /gpt
def gpt(update: Update, context: CallbackContext) -> None:
    message = ' '.join(context.args)
    response = openai.Completion.create(
        engine="text-davinci-003",  # Chọn engine GPT bạn muốn dùng
        prompt=message,
        max_tokens=150
    )
    update.message.reply_text(response.choices[0].text.strip())

# Hàm xử lý lệnh /grok
def grok(update: Update, context: CallbackContext) -> None:
    message = ' '.join(context.args)
    response = requests.post(
        "https://api.grok.com/your-endpoint",  # Thay đổi endpoint và API key thực tế của bạn
        json={"prompt": message}
    )
    result = response.json()
    update.message.reply_text(result['response'])

# Hàm xử lý lệnh /gemini
def gemini(update: Update, context: CallbackContext) -> None:
    message = ' '.join(context.args)
    response = requests.post(
        "https://api.gemini.com/your-endpoint",  # Thay đổi endpoint và API key thực tế của bạn
        json={"prompt": message}
    )
    result = response.json()
    update.message.reply_text(result['response'])

def main() -> None:
    # Thêm token của bot
    updater = Updater("YOUR_BOT_API_TOKEN")
    
    dispatcher = updater.dispatcher

    # Các handler cho các lệnh
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("gpt", gpt))
    dispatcher.add_handler(CommandHandler("grok", grok))
    dispatcher.add_handler(CommandHandler("gemini", gemini))

    # Bắt đầu bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
