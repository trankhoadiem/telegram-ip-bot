from telegram import Update 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import sys
from openai import OpenAI
import google.generativeai as genai

# ==== TOKEN & API KEYS ====
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = os.environ.get("XAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

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

# chọn model
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gpt"
    await update.message.reply_text("🧠 Bạn đang trò chuyện với **ChatGPT**.")

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "grok"
    await update.message.reply_text("🦉 Bạn đang trò chuyện với **Grok**.")

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gemini"
    await update.message.reply_text("🌌 Bạn đang trò chuyện với **Gemini**.")

# ==== Hàm gọi AI ====
async def chat_gpt(query: str) -> str:
    if not OPENAI_API_KEY:
        return "❌ GPT lỗi: Thiếu OPENAI_API_KEY"
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": query}],
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"⚠️ GPT lỗi: {e}"

async def chat_grok(query: str) -> str:
    if not XAI_API_KEY:
        return "❌ GROK lỗi: Thiếu XAI_API_KEY"
    try:
        resp = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {XAI_API_KEY}"},
            json={
                "model": "grok-2",
                "messages": [{"role": "user", "content": query}],
            },
            timeout=30,
        )
        data = resp.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"]
        return f"⚠️ GROK trả về lỗi: {data}"
    except Exception as e:
        return f"⚠️ GROK lỗi: {e}"

async def chat_gemini(query: str) -> str:
    if not GOOGLE_API_KEY:
        return "❌ GEMINI lỗi: Thiếu GOOGLE_API_KEY"
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(query)
        return resp.text
    except Exception as e:
        return f"⚠️ GEMINI lỗi: {e}"

# xử lý tin nhắn khi đang trong chế độ AI
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return

    query = update.message.text.strip()
    thinking_msg = await update.message.reply_text("⏳ Đang suy nghĩ...")

    if mode == "gpt":
        reply = await chat_gpt(query)
    elif mode == "grok":
        reply = await chat_grok(query)
    elif mode == "gemini":
        reply = await chat_gemini(query)
    else:
        reply = "⚠️ Chưa chọn model AI."

    await thinking_msg.edit_text(reply)

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
# 🚀 Test API
# =======================
async def test_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results = []

    # GPT
    try:
        if not OPENAI_API_KEY:
            results.append("OPENAI: ❌ missing")
        else:
            client = OpenAI(api_key=OPENAI_API_KEY)
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
            )
            results.append("OPENAI: ✅ OK")
    except Exception as e:
        results.append(f"OPENAI: ⚠️ {e}")

    # GROK
    try:
        if not XAI_API_KEY:
            results.append("GROK: ❌ missing")
        else:
            resp = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {XAI_API_KEY}"},
                json={"model": "grok-2", "messages": [{"role": "user", "content": "ping"}]},
                timeout=20,
            )
            if resp.status_code == 200:
                results.append("GROK: ✅ OK")
            else:
                results.append(f"GROK: ⚠️ {resp.status_code} {resp.text}")
    except Exception as e:
        results.append(f"GROK: ⚠️ {e}")

    # GEMINI
    try:
        if not GOOGLE_API_KEY:
            results.append("GEMINI: ❌ missing")
        else:
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content("ping")
            if resp.text:
                results.append("GEMINI: ✅ OK")
            else:
                results.append("GEMINI: ⚠️ No response")
    except Exception as e:
        results.append(f"GEMINI: ⚠️ {e}")

    await update.message.reply_text("🔎 Kết quả kiểm tra API:\n" + "\n".join(results))

# =======================
# 🚀 Các lệnh khác
# =======================
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini)\n\n"
        "⚡ Bot vẫn đang **cập nhật hằng ngày**, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng."
    )

async def help_command(update, context):
    await update.message.reply_text(
        "📖 **Danh sách lệnh khả dụng**:\n\n"
        "🚀 /start - Bắt đầu\n"
        "🛠 /help - Trợ giúp\n"
        "🤖 /ai - Bật Chế độ AI\n"
        "🌐 /ip <ip> - Kiểm tra IP\n"
        "🎬 /tiktok <link> - Tải TikTok\n"
        "🔧 /testapi - Kiểm tra API keys\n\n"
        "🔒 Admin:\n"
        "🛑 /shutdown\n"
        "♻️ /restart\n"
        "✅ /startbot"
    )

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
            await waiting_msg.edit_text("❌ Không tải được TikTok.")
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

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"🎉👋 Chào mừng {member.full_name}!")

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
    app.add_handler(CommandHandler("testapi", test_api))

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
