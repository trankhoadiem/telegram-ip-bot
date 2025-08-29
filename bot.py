from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import openai
import os

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

# ==== API Key OpenAI ====
openai.api_key = os.getenv("OPENAI_API_KEY")

# ==== Trạng thái người dùng cho Gemini ====
user_sessions = {}

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ tra cứu IP & tải TikTok video/ảnh chất lượng cao.\n\n"
        "📌 Các thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/tiktok <link> - Tải video/ảnh TikTok chất lượng cao\n"
        "/testapi - Kiểm tra kết nối với API\n"
        "/ai - Vào chế độ Chat AI (chỉ /gemini hoạt động)\n"
        "/gemini - Chế độ Gemini AI (chat liên tục)\n"
        "/grok - Đang bảo trì\n"
        "/gpt - Đang bảo trì\n"
        "/seek - Đang bảo trì\n"
        "/exit - Thoát chế độ Chat AI"
    )

# ==== /gemini ====
async def gemini(update, context):
    user_id = update.message.from_user.id
    user_sessions[user_id] = True
    await update.message.reply_text(
        "🌟 Bạn đã vào chế độ Gemini AI! Nhắn tin gì đi, bot sẽ trả lời bạn. "
        "Gõ /exit để thoát chế độ chat."
    )

# ==== /exit ====
async def exit_chat(update, context):
    user_id = update.message.from_user.id
    if user_sessions.get(user_id):
        user_sessions.pop(user_id, None)
        await update.message.reply_text("✅ Bạn đã thoát chế độ Gemini AI.")
    else:
        await update.message.reply_text("⚠️ Bạn không đang trong chế độ Chat AI.")

# ==== Xử lý tin nhắn khi đang chat Gemini ====
async def handle_message(update, context):
    user_id = update.message.from_user.id
    if user_sessions.get(user_id):  # Kiểm tra người dùng có đang ở chế độ Gemini hay không
        user_input = update.message.text

        try:
            # Gọi API OpenAI để nhận câu trả lời từ GPT
            response = openai.Completion.create(
                engine="text-davinci-003",  # Bạn có thể thay đổi model này nếu dùng GPT-4 hoặc model khác
                prompt=user_input,
                max_tokens=150,
                temperature=0.7
            )

            # Nhận câu trả lời từ API và gửi lại
            reply = response.choices[0].text.strip()
            await update.message.reply_text(reply)
        
        except Exception as e:
            await update.message.reply_text(f"⚠️ Đã có lỗi khi kết nối với AI: {e}")

# ==== /testapi ====
async def testapi(update, context):
    try:
        url = "https://myapi.com/status"  # Thay bằng API của bạn
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            await update.message.reply_text("✅ Kết nối API thành công! API đang hoạt động bình thường.")
        else:
            await update.message.reply_text(f"⚠️ API không phản hồi đúng. Mã lỗi: {response.status_code}")
    except requests.RequestException as e:
        await update.message.reply_text(f"❌ Lỗi kết nối API: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("testapi", testapi))
    app.add_handler(CommandHandler("ai", help_command))  # /ai là lệnh vào chế độ Chat AI
    app.add_handler(CommandHandler("gemini", gemini))
    app.add_handler(CommandHandler("exit", exit_chat))

    # Message handler for Gemini chat
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
