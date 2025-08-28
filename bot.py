import openai
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Lấy API Key từ biến môi trường (cấu hình trong Railway)
openai.api_key = os.getenv("OPENAI_API_KEY")  # Sử dụng OPENAI_API_KEY từ Railway
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Sử dụng TELEGRAM_TOKEN từ Railway

# Hàm xử lý /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào mừng bạn đến với bot GPT-3!\n\nGửi câu hỏi để tôi trả lời."
    )

# Hàm xử lý tin nhắn
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text  # Câu hỏi người dùng gửi
    try:
        # Gọi OpenAI API để nhận câu trả lời với cách gọi mới
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Bạn có thể thay đổi model nếu cần
            messages=[{"role": "user", "content": user_message}],
            max_tokens=150
        )
        answer = response['choices'][0]['message']['content'].strip()  # Lấy câu trả lời từ GPT-3
        await update.message.reply_text(answer)
    
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi kết nối với GPT-3: {e}")

# Cấu hình bot Telegram
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()  # Lấy token từ biến môi trường

    # Lệnh start
    app.add_handler(CommandHandler("start", start))

    # Lắng nghe tin nhắn người dùng và trả lời
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()

if __name__ == "__main__":
    main()
