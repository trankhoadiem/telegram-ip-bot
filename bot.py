from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==== TOKEN Telegram ====
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Thay YOUR_TELEGRAM_BOT_TOKEN bằng token của bot của bạn

# ==== /start Command ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Chào mừng bạn đến với Bot Chat! Bạn có thể hỏi tôi bất kỳ câu hỏi nào!"
    )

# ==== Hàm trả lời câu hỏi đơn giản ====
async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text  # Lấy tin nhắn người dùng

    # Trả lời câu hỏi dựa trên một số mẫu câu
    if "hello" in user_message.lower():
        await update.message.reply_text("Chào bạn! Bạn cần giúp gì?")
    elif "how are you" in user_message.lower():
        await update.message.reply_text("Tôi rất khỏe, cảm ơn bạn đã hỏi!")
    elif "bye" in user_message.lower():
        await update.message.reply_text("Tạm biệt! Hẹn gặp lại bạn sau!")
    else:
        await update.message.reply_text("Bạn vừa hỏi: " + user_message)

# ==== Main Function ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Các lệnh và xử lý tin nhắn
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))  # Xử lý tất cả các tin nhắn văn bản

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
