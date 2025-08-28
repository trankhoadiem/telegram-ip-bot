from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import openai
import google.generativeai as genai

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")   # ChatGPT
XAI_API_KEY = os.environ.get("XAI_API_KEY")         # Grok
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")   # Gemini

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# =======================
# 🚀 AI Commands
# =======================

# /ai (chế độ AI)
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Đã chuyển sang **chế độ AI**.\n\n"
        "👉 Hãy chọn chế độ bạn muốn dùng:\n"
        "/gpt - Chat GPT\n"
        "/grok - Chat Grok\n"
        "/gemini - Chat Gemini\n"
        "/exit - Thoát chế độ AI"
    )

# /exit (thoát chế độ AI)
async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bạn đã thoát khỏi **chế độ AI**.")

# GPT
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /gpt <câu hỏi>")
        return
    query = " ".join(context.args)
    try:
        openai.api_key = OPENAI_API_KEY
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}]
        )
        reply = res.choices[0].message["content"]
        await update.message.reply_text(
            f"🤖 Chat GPT đang trả lời...\n\n{reply}\n\n---\n👮 Admin: @DuRinn_LeTuanDiem"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi GPT: {e}")

# Grok
async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /grok <câu hỏi>")
        return
    query = " ".join(context.args)
    try:
        headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json={"model": "grok-beta", "messages": [{"role": "user", "content": query}]}
        )
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]
        await update.message.reply_text(
            f"🦉 Chat Grok đang trả lời...\n\n{reply}\n\n---\n👮 Admin: @DuRinn_LeTuanDiem"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi Grok: {e}")

# Gemini
async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /gemini <câu hỏi>")
        return
    query = " ".join(context.args)
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-pro")
        resp = model.generate_content(query)
        await update.message.reply_text(
            f"🌌 Chat Gemini đang trả lời...\n\n{resp.text}\n\n---\n👮 Admin: @DuRinn_LeTuanDiem"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi Gemini: {e}")

# =======================
# 🚀 Các lệnh sẵn có
# =======================

# /start
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ tra cứu IP, tải TikTok video/ảnh chất lượng cao & chat AI (GPT, Grok, Gemini).\n\n"
        "📌 Các thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# /help (chỉ còn /ai)
async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ai - Chuyển sang chế độ AI (GPT, Grok, Gemini)\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/tiktok <link> - Tải video/ảnh TikTok"
    )

# Check IP
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

# TikTok Downloader
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
# 🚀 Main
# =======================
def main():
    app = Application.builder().token(TOKEN).build()

    # AI
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("exit", exit_ai))
    app.add_handler(CommandHandler("gpt", gpt))
    app.add_handler(CommandHandler("grok", grok))
    app.add_handler(CommandHandler("gemini", gemini))

    # Tools
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()