from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import sys
import openai
import google.generativeai as genai
import asyncio

# ==== TOKEN & API KEYS ====
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = os.environ.get("XAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")   # Gemini key

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# =======================
# 🚀 Hàm xóa tin nhắn sau 5 phút
# =======================
async def delete_after_delay(context: ContextTypes.DEFAULT_TYPE, chat_id, msg_ids):
    await asyncio.sleep(300)  # 5 phút
    for mid in msg_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except:
            pass

# =======================
# 🚀 AI MODE
# =======================

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    msg = await update.message.reply_text(
        "🤖 Đã bật **Chế độ AI**\n\n"
        "👉 Chọn model để trò chuyện:\n"
        "🧠 /gpt - ChatGPT\n"
        "🦉 /grok - Grok\n"
        "🌌 /gemini - Gemini\n"
        "❌ /exit - Thoát chế độ AI\n\n"
        "⏳ Tin nhắn sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [update.message.message_id, msg.message_id]))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    msg = await update.message.reply_text("✅ Bạn đã thoát khỏi **Chế độ AI**.\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [update.message.message_id, msg.message_id]))

# chọn model
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gpt"
    msg = await update.message.reply_text("🧠 Bạn đang trò chuyện với **ChatGPT**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [update.message.message_id, msg.message_id]))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "grok"
    msg = await update.message.reply_text("🦉 Bạn đang trò chuyện với **Grok**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [update.message.message_id, msg.message_id]))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gemini"
    msg = await update.message.reply_text("🌌 Bạn đang trò chuyện với **Gemini**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [update.message.message_id, msg.message_id]))

# xử lý tin nhắn khi đang trong chế độ AI
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return

    query = update.message.text.strip()
    thinking_msg = await update.message.reply_text("⏳ Đang suy nghĩ...")
    
    try:
        await update.message.delete()  # xoá tin nhắn user ngay
    except:
        pass

    try:
        if mode == "gpt":
            openai.api_key = OPENAI_API_KEY
            res = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}]
            )
            reply = res.choices[0].message["content"]

        elif mode == "grok":
            headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
            resp = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json={"model": "grok-4-0709", "messages": [{"role": "user", "content": query}]}
            )
            data = resp.json()
            reply = data["choices"][0]["message"]["content"]

        elif mode == "gemini":
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(query)
            reply = resp.text

        else:
            reply = "⚠️ Chưa chọn model AI."
    except Exception as e:
        reply = f"⚠️ Lỗi {mode.upper()}: {e}"

    final_msg = await thinking_msg.edit_text(reply + "\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [final_msg.message_id]))

# =======================
# 🚀 Admin Commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("🛑 Bot đang **tắt**...")

    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("♻️ Bot đang **khởi động lại**...")
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("✅ Bot đang chạy bình thường!")

# =======================
# 🚀 Các lệnh khác (start, help, ip, tiktok, welcome)
# =======================
# (các hàm của bạn vẫn giữ nguyên, chỉ cần thêm câu "⏳ Tin nhắn sẽ tự động xóa sau 5 phút." và gọi delete_after_delay như mẫu trên nếu muốn xoá luôn)

# =======================
# 🚀 MAIN
# =======================
def main():
    app = Application.builder().token(TOKEN).build()

    # AI
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("exit", exit_ai))
    app.add_handler(CommandHandler("gpt", gpt))
    app.add_handler(CommandHandler("grok", grok))
    app.add_handler(CommandHandler("gemini", gemini))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))

    # Tools
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))

    # Admin
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))

    # Welcome
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
