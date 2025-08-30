from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import sys
import openai
import google.generativeai as genai

# ==== TOKEN & API KEYS ====
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = os.environ.get("XAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

# ==== ADMIN ====
ADMIN_USERNAME = "Tominhdiem"   # username Telegram của anh

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
# 🚀 Xóa tin nhắn người dùng sau khi gọi lệnh
# =======================
async def delete_user_message(update: Update):
    try:
        await update.message.delete()
    except:
        pass

# =======================
# 🚀 AI MODE
# =======================
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = None
    await update.message.reply_text(
        "🤖 Đã bật **Chế độ AI**\n\n"
        "👉 Chọn model:\n"
        "🧠 /gpt\n"
        "🦉 /grok\n"
        "🌌 /gemini\n"
        "❌ /exit"
    )

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = None
    await update.message.reply_text("✅ Đã thoát khỏi **Chế độ AI**.")

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = "gpt"
    await update.message.reply_text("🧠 Đang dùng **ChatGPT**.")

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = "grok"
    await update.message.reply_text("🦉 Đang dùng **Grok**.")

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = "gemini"
    await update.message.reply_text("🌌 Đang dùng **Gemini**.")

async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return
    query = update.message.text.strip()
    thinking_msg = await update.message.reply_text("⏳ Đang suy nghĩ...")
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
            reply = "⚠️ Chưa chọn model."
    except Exception as e:
        reply = f"⚠️ Lỗi {mode.upper()}: {e}"

    await thinking_msg.edit_text(reply)

# =======================
# 🚀 Admin Commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Không có quyền.")
        return
    await update.message.reply_text("🛑 Bot tắt...")
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Không có quyền.")
        return
    await update.message.reply_text("♻️ Restart bot...")
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Không có quyền.")
        return
    await update.message.reply_text("✅ Bot đang chạy!")

# =======================
# 🚀 Commands
# =======================
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng đến với BOT** ✨\n\n"
        "🤖 Công cụ hỗ trợ:\n"
        "🌐 /ip <ip>\n"
        "🎬 /tiktok <link>\n"
        "📱 /tiktokinfo <username>\n"
        "🤖 /ai - Chat AI (GPT, Grok, Gemini)\n\n"
        "👤 Phát triển bởi: **Tô Minh Điềm**"
    )

async def check_ip(update, context):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0].strip()
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            await update.message.reply_text(f"❌ Không tìm thấy thông tin IP: {ip}")
            return
        info = (
            f"🌐 Thông tin IP {res['query']}:\n"
            f"🏳️ Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Thành phố: {res['regionName']} - {res['city']}\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📡 ISP: {res['isp']}\n"
            f"🏢 Tổ chức: {res['org']}"
        )
        flag_url = f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png"
        await update.message.reply_photo(flag_url, caption=info)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi kiểm tra IP: {e}")

async def download_tiktok(update, context):
    await delete_user_message(update)
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

async def tiktok_info(update, context):
    await delete_user_message(update)   # ✅ auto delete tin nhắn user
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktokinfo <username>")
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy thông tin TikTok @{username}...")
    try:
        api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
        res = requests.get(api_url, headers=HEADERS, timeout=15).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Không lấy được thông tin TikTok!")
            return

        user = res["data"]
        avatar = user.get("avatar", "")
        nickname = user.get("nickname", "N/A")
        uid = user.get("unique_id", "N/A")
        secid = user.get("sec_uid", "N/A")
        followers = user.get("follower_count", 0)
        following = user.get("following_count", 0)
        heart = user.get("total_favorited", 0)
        video_count = user.get("aweme_count", 0)
        bio = user.get("signature", "Không có")
        region = user.get("region", "N/A")
        verified = "✅ Có" if user.get("verified") else "❌ Không"
        birthday = user.get("birthday", "Không công khai")
        create_time = user.get("create_time", "N/A")

        caption = (
            f"📱 Thông tin TikTok @{uid}:\n"
            f"👤 Tên: {nickname}\n"
            f"🆔 Sec-UID: {secid}\n"
            f"🌍 Quốc gia: {region}\n"
            f"✔️ Verified: {verified}\n"
            f"🎂 Ngày sinh: {birthday}\n"
            f"📅 Ngày tạo: {create_time}\n"
            f"👥 Followers: {followers}\n"
            f"👤 Following: {following}\n"
            f"❤️ Tổng like: {heart}\n"
            f"🎬 Số video: {video_count}\n"
            f"📝 Bio: {bio}"
        )

        if avatar:
            await waiting_msg.delete()
            await update.message.reply_photo(avatar, caption=caption)
        else:
            await waiting_msg.edit_text(caption)
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi lấy TikTok info: {e}")

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
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("tiktokinfo", tiktok_info))

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
