from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import openai
import google.generativeai as genai

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = os.environ.get("XAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"   # check bằng username

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
# 🚀 AI MODE
# =======================

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    await update.message.reply_text(
        "🤖 Đã bật **chế độ AI**.\n\n"
        "👉 Chọn model:\n"
        "/gpt - Chat GPT\n"
        "/grok - Chat Grok\n"
        "/gemini - Chat Gemini\n"
        "/exit - Thoát chế độ AI"
    )

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    await update.message.reply_text("✅ Bạn đã thoát **chế độ AI**.")

# chọn model
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gpt"
    await update.message.reply_text("👉 Bạn đang chat với **ChatGPT**. Nhập tin nhắn... (/exit để thoát)")

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "grok"
    await update.message.reply_text("👉 Bạn đang chat với **Grok**. Nhập tin nhắn... (/exit để thoát)")

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gemini"
    await update.message.reply_text("👉 Bạn đang chat với **Gemini**. Nhập tin nhắn... (/exit để thoát)")

# xử lý tin nhắn khi đang trong chế độ AI
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return  # không trong AI mode thì bỏ qua

    query = update.message.text.strip()
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
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(query)
            reply = resp.text

        else:
            reply = "⚠️ Chưa chọn model AI."
    except Exception as e:
        reply = f"⚠️ Lỗi {mode.upper()}: {e}"

    await update.message.reply_text(reply)

# =======================
# 🚀 Admin Commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("🛑 Bot đang tắt...")
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("♻️ Bot đang khởi động lại...")
    await context.application.stop()
    # Thực tế restart cần systemd/pm2/docker, ở đây chỉ stop

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("✅ Bot đang chạy bình thường!")

# =======================
# 🚀 Các lệnh khác
# =======================

# /start
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ tra cứu IP, tải TikTok video/ảnh chất lượng cao & chat AI (GPT, Grok, Gemini).\n\n"
        "⚡ Bot vẫn đang **cập nhật hằng ngày**, nên có thể sẽ tồn tại một số lỗi trong quá trình sử dụng.\n\n"
        "📌 Các thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# /help
async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ai - Chế độ AI (GPT, Grok, Gemini)\n"
        "/ip <ip> - Kiểm tra IP\n"
        "/tiktok <link> - Tải TikTok\n\n"
        "🔒 Lệnh dành cho Admin: @DuRinn_LeTuanDiem\n"
        "/shutdown - Tắt bot\n"
        "/restart - Khởi động lại bot\n"
        "/startbot - Kiểm tra/bật bot"
    )

# IP lookup
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"
        info = (
            f"🌍 Thông tin IP {res['query']}:\n"
            f"🗺 Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Khu vực: {res['regionName']} - {res['city']} ({res.get('zip','')})\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📍 Toạ độ: {res['lat']}, {res['lon']}\n"
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
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=info)
    else:
        await update.message.reply_text(info)

# TikTok downloader
async def download_tiktok(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>")
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20)
        data_json = res.json()
        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text("❌ Không tải được TikTok. Vui lòng kiểm tra lại link!")
            return
        data = data_json["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title} (HQ)")
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# Welcome New Member
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🎉 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!"
        )

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

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
