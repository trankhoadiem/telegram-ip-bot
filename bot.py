from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import sys
import openai
import google.generativeai as genai
import re

# ==== TOKEN & API KEYS ====
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = os.environ.get("XAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN")   # Facebook Graph API token (bắt buộc cho /facebook)

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
# 🚀 AI MODE
# =======================
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    await update.message.reply_text(
        "🤖 Đã bật **Chế độ AI**\n\n"
        "👉 Chọn model để trò chuyện:\n"
        "🧠 /gpt - ChatGPT\n"
        "🦉 /grok - Grok\n"
        "🌌 /gemini - Gemini\n"
        "❌ /exit - Thoát chế độ AI"
    )

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    await update.message.reply_text("✅ Bạn đã thoát khỏi **Chế độ AI**.")

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gpt"
    await update.message.reply_text("🧠 Bạn đang trò chuyện với **ChatGPT**.")

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "grok"
    await update.message.reply_text("🦉 Bạn đang trò chuyện với **Grok**.")

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gemini"
    await update.message.reply_text("🌌 Bạn đang trò chuyện với **Gemini**.")

async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return
    query = update.message.text.strip()
    thinking_msg = await update.message.reply_text("⏳ Đang suy nghĩ...")
    try:
        await update.message.delete()
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

    await thinking_msg.edit_text(reply)

# =======================
# 🚀 Admin Commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền.")
        return
    await update.message.reply_text("🛑 Bot đang tắt...")
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền.")
        return
    await update.message.reply_text("♻️ Bot đang khởi động lại...")
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền.")
        return
    await update.message.reply_text("✅ Bot đang chạy!")

# =======================
# 🚀 Commands
# =======================
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng đến với BOT** ✨\n\n"
        "Lệnh có sẵn:\n"
        "🤖 /ai - Chat AI\n"
        "🌐 /ip <ip>\n"
        "🎬 /tiktok <link>\n"
        "📘 /facebook <id hoặc link>\n\n"
        "🔒 Lệnh admin: /shutdown, /restart, /startbot"
    )

async def help_command(update, context):
    await update.message.reply_text("📖 /ip, /tiktok, /ai, /facebook, /help")

# ==== Check IP ====
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
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=info)
    else:
        await update.message.reply_text(info)

# ==== TikTok ====
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
            await waiting_msg.edit_text("❌ Không tải được TikTok!")
            return
        data = data_json["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title}")
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi: {e}")

# ==== Facebook ====
def extract_fbid(text):
    # Lấy id từ link facebook.com/username hoặc trực tiếp id
    if re.match(r'^\d+$', text):
        return text
    if "facebook.com" in text:
        parts = text.split("/")
        for p in parts:
            if p and p.isdigit():
                return p
    return text

async def check_facebook(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /facebook <id hoặc link>")
        return
    fid = extract_fbid(context.args[0])
    url = f"https://graph.facebook.com/v17.0/{fid}?fields=id,name,link,birthday,about&access_token={FACEBOOK_TOKEN}"
    try:
        res = requests.get(url, timeout=15).json()
        if "error" in res:
            await update.message.reply_text(f"❌ Lỗi: {res['error'].get('message')}")
            return
        name = res.get("name", "N/A")
        fb_link = res.get("link", "N/A")
        birthday = res.get("birthday", "Không công khai")
        about = res.get("about", "Không có")
        caption = (
            f"📘 Thông tin Facebook:\n"
            f"👤 Tên: {name}\n"
            f"🔗 Link: {fb_link}\n"
            f"🎂 Ngày sinh: {birthday}\n"
            f"ℹ️ Giới thiệu: {about}"
        )
        # Lấy avatar
        avatar_url = f"https://graph.facebook.com/{fid}/picture?type=large&access_token={FACEBOOK_TOKEN}"
        await update.message.reply_photo(avatar_url, caption=caption)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi lấy thông tin FB: {e}")

# ==== Welcome ====
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"🎉👋 Chào mừng {member.full_name} vào nhóm {update.message.chat.title}!")

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
    app.add_handler(CommandHandler("facebook", check_facebook))

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
