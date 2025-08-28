import openai
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==== API Keys ====
TOKEN = os.environ.get("TELEGRAM_TOKEN")  # Token của bot Telegram từ biến môi trường
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")  # Key của OpenAI từ biến môi trường

# Cấu hình OpenAI
openai.api_key = OPENAI_API_KEY

# ==== /start Command ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Chào mừng bạn đến với bot AI Chat! ✨\n\n"
        "🤖 Hỏi gì, bot trả lời đó như ChatGPT.\n"
        "💡 Gõ câu hỏi và bot sẽ trả lời tự động.\n"
        "🛠 Dùng lệnh /testapi để kiểm tra kết nối với OpenAI API."
    )

# ==== /testapi Command ====
async def test_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Gửi yêu cầu đơn giản đến OpenAI API để kiểm tra kết nối
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Hoặc gpt-4 nếu bạn có quyền truy cập
            messages=[{"role": "user", "content": "Hello"}]  # Định dạng mới của API
        )
        
        if response:
            await update.message.reply_text("✅ API OpenAI kết nối thành công!")
        else:
            await update.message.reply_text("⚠️ Không thể kết nối tới API OpenAI. Vui lòng kiểm tra lại.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi khi kết nối API: {e}")

# ==== Xử lý tin nhắn người dùng ====
async def chat_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text  # Lấy tin nhắn của người dùng

    try:
        # Gửi yêu cầu đến OpenAI để nhận câu trả lời
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Hoặc gpt-4 nếu bạn có quyền truy cập
            messages=[{"role": "user", "content": user_message}],
            max_tokens=150,  # Giới hạn số token của phản hồi
            temperature=0.7  # Điều chỉnh độ sáng tạo của câu trả lời
        )
        
        answer = response['choices'][0]['message']['content'].strip()
        await update.message.reply_text(answer)
    
    except openai.error.OpenAIError as e:
        # Xử lý lỗi từ OpenAI
        await update.message.reply_text(f"❌ Lỗi OpenAI: {e}")
    except Exception as e:
        # Xử lý các lỗi chung khác
        await update.message.reply_text(f"❌ Đã xảy ra lỗi: {e}")

# ==== Main Function ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Command
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("testapi", test_api))  # Thêm handler cho lệnh /testapi

    # Message Handler: Xử lý tất cả tin nhắn và trả lời bằng GPT
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat_gpt))

    print("🤖 Bot AI Chat đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
