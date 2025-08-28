from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")  # Lấy token từ biến môi trường

# ==== /start Command ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "Bot hiện đang trong trạng thái bảo trì và sẽ sớm hoạt động lại. Cảm ơn bạn đã thông cảm."
    )

# ==== Bảo trì: Tự động trả lời tin nhắn ====
async def maintenance_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚠️ Bot hiện đang trong trạng thái bảo trì. Xin vui lòng thử lại sau!"
    )

# ==== Main Function ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Command
    app.add_handler(CommandHandler("start", start))

    # Message Handler: Chặn tất cả tin nhắn và gửi thông báo bảo trì
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, maintenance_reply))

    print("🤖 Bot đang chạy trong chế độ bảo trì...")
    app.run_polling()

if __name__ == "__main__":
    main()
