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
# 🚀 Hàm xoá tin nhắn
# =======================
async def delete_after_delay(context: ContextTypes.DEFAULT_TYPE, chat_id, msg_ids):
    """Xoá tin nhắn bot sau 5 phút"""
    await asyncio.sleep(300)
    for mid in msg_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except:
            pass

async def auto_delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Xoá ngay tin nhắn user"""
    if update.message:
        try:
            await update.message.delete()
        except:
            pass

# =======================
# 🚀 Clear all messages
# =======================
async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    
    chat_id = update.effective_chat.id
    notice = await update.message.reply_text("🧹 Đang xóa tất cả tin nhắn cũ...")
    try:
        async for msg in context.bot.get_chat_history(chat_id, limit=500):
            try:
                await context.bot.delete_message(chat_id, msg.message_id)
            except:
                pass
        done = await update.message.reply_text("✅ Đã xoá xong toàn bộ tin nhắn gần nhất!\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, chat_id, [notice.message_id, done.message_id]))
    except Exception as e:
        err = await update.message.reply_text(f"⚠️ Lỗi khi xóa: {e}")
        context.application.create_task(delete_after_delay(context, chat_id, [notice.message_id, err.message_id]))

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
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    msg = await update.message.reply_text("✅ Bạn đã thoát khỏi **Chế độ AI**.\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

# chọn model
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gpt"
    msg = await update.message.reply_text("🧠 Bạn đang trò chuyện với **ChatGPT**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "grok"
    msg = await update.message.reply_text("🦉 Bạn đang trò chuyện với **Grok**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gemini"
    msg = await update.message.reply_text("🌌 Bạn đang trò chuyện với **Gemini**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

# xử lý tin nhắn khi đang trong chế độ AI
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return

    query = update.message.text.strip()
    thinking_msg = await update.message.reply_text("⏳ Đang suy nghĩ...")

    try:
        await update.message.delete()  # xoá user ngay
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
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
        return
    msg = await update.message.reply_text("🛑 Bot đang **tắt**...")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
        return
    msg = await update.message.reply_text("♻️ Bot đang **khởi động lại**...")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
        return
    msg = await update.message.reply_text("✅ Bot đang chạy bình thường!\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

# =======================
# 🚀 Các lệnh khác
# =======================
async def start(update, context):
    msg = await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini)\n\n"
        "⚡ Bot vẫn đang **cập nhật hằng ngày**, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng.\n\n"
        "⏳ Tin nhắn sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

async def help_command(update, context):
    msg = await update.message.reply_text(
        "📖 **Danh sách lệnh khả dụng**:\n\n"
        "🚀 /start - Bắt đầu\n"
        "🛠 /help - Trợ giúp\n"
        "🤖 /ai - Bật Chế độ AI (GPT, Grok, Gemini)\n"
        "🌐 /ip <ip> - Kiểm tra IP\n"
        "🎬 /tiktok <link> - Tải TikTok\n\n"
        "🔒 **Lệnh Admin** (@DuRinn_LeTuanDiem):\n"
        "🛑 /shutdown - Tắt bot\n"
        "♻️ /restart - Khởi động lại bot\n"
        "✅ /startbot - Kiểm tra bot\n"
        "🧹 /clear - Xoá toàn bộ tin nhắn cũ\n\n"
        "⏳ Tin nhắn sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"
        info = (
            f"🌐 Thông tin IP {res['query']}:\n"
            f"🏳️ Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Thành phố: {res['regionName']} - {res['city']} ({res.get('zip','')})\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📍 Tọa độ: {res['lat']}, {res['lon']}\n"
            f"📡 ISP: {res['isp']}\n"
            f"🏢 Tổ chức: {res['org']}\n"
            f"🔗 AS: {res['as']}"
        )
        flag_url = f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png"
        return flag_url, info
    except Exception as e:
        return None, f"⚠️ Lỗi khi kiểm tra IP: {e}"

async def check_ip(update, context):
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /ip 8.8.8.8\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        msg = await update.message.reply_photo(flag_url, caption=info + "\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
    else:
        msg = await update.message.reply_text(info + "\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

async def download_tiktok(update, context):
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20)
        data_json = res.json()
        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text("❌ Không tải được TikTok. Vui lòng kiểm tra lại link!\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
            context.application.create_task(delete_after_delay(context, update.effective_chat.id, [waiting_msg.message_id]))
            return
        data = data_json["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            msg = await update.message.reply_video(url, caption=f"🎬 {title} (HQ)\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh...")
            msg = None
            for img_url in data["images"]:
                m = await update.message.reply_photo(img_url, caption="⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
                context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
            context.application.create_task(delete_after_delay(context, update.effective_chat.id, [waiting_msg.message_id]))
            return
        if msg:
            context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [waiting_msg.message_id]))

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        msg = await update.message.reply_text(
            f"🎉👋 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút."
        )
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

# =======================
# 🚀 MAIN
# =======================
def main():
    app = Application.builder().token(TOKEN).build()

    # Xoá ngay tin nhắn user
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, auto_delete_user), group=-1)

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
    app.add_handler(CommandHandler("clear", clear_chat))

    # Welcome
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
