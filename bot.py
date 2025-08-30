# bot.py
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import requests, os, sys, asyncio

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

# ==== Helper ====
async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except:
        pass

async def auto_delete(msg, delay=30):
    """Xóa tin nhắn bot sau delay giây"""
    try:
        await asyncio.sleep(delay)
        await msg.delete()
    except:
        pass

# =======================
# 🔧 AI MODE
# =======================
MAINT_MSG = (
    "🔧 *Chức năng AI hiện đang bảo trì & nâng cấp*\n\n"
    "Các model AI như ChatGPT, Grok, Gemini tạm thời không hoạt động.\n\n"
    "📌 Bạn vẫn có thể dùng: /ip, /tiktok, /tiktokinfo.\n"
    "⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
)

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text("✅ Đã thoát khỏi chế độ AI.\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg))

# =======================
# 🔒 Admin commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("🛑 Bot đang tắt...\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("♻️ Bot đang khởi động lại...\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("✅ Bot đang chạy bình thường!\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

# =======================
# 🚀 Start / Help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    text = (
        "✨ **Chào mừng bạn đến với BOT Pro** ✨\n\n"
        "⚡ Bot được cập nhật liên tục, hoạt động ổn định.\n"
        "📌 Thành viên phát triển:\n"
        "   👤 Tô Minh Điềm – @DuRinn_LeTuanDiem\n"
        "💡 Gõ /help để xem tất cả lệnh.\n"
        "⏳ Tin nhắn này sẽ tự động xoá sau 10 giây"
    )
    msg = await update.message.reply_text(text)
    asyncio.create_task(auto_delete(msg, delay=10))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

    keyboard = [
        [KeyboardButton("/ip")],
        [KeyboardButton("/tiktok"), KeyboardButton("/tiktokinfo")],
        [KeyboardButton("/ai"), KeyboardButton("/exit")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    text = (
        "📖 **Hướng dẫn sử dụng BOT Pro** 📖\n\n"
        "🚀 **Lệnh cơ bản**:\n"
        "   • /start — Giới thiệu BOT.\n"
        "   • /help — Hiển thị hướng dẫn chi tiết.\n\n"
        "🤖 **Chế độ AI** (🔧 bảo trì):\n"
        "   • /ai — Bật chế độ AI.\n"
        "   • /gpt — ChatGPT.\n"
        "   • /grok — Grok.\n"
        "   • /gemini — Gemini.\n"
        "   • /exit — Thoát chế độ AI.\n\n"
        "🌐 **Công cụ IP**:\n"
        "   • /ip <ip> — Xem thông tin IP.\n\n"
        "🎬 **Công cụ TikTok**:\n"
        "   • /tiktok <link> — Tải video/ảnh TikTok.\n"
        "   • /tiktokinfo <username> — Lấy info TikTok.\n\n"
        "⚠️ Tin nhắn này sẽ tự động xoá sau 30 giây"
    )

    msg = await update.message.reply_text(text, reply_markup=reply_markup)
    asyncio.create_task(auto_delete(msg))

# =======================
# 🌐 IP checker
# =======================
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy IP: {ip}"
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
        return f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png", info
    except Exception as e:
        return None, f"⚠️ Lỗi IP: {e}"

async def check_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /ip <địa_chỉ_ip>\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        msg = await update.message.reply_photo(flag_url, caption=info + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    else:
        msg = await update.message.reply_text(info + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

# =======================
# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /tiktok <link>\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok... Tin nhắn này sẽ tự động xoá sau 30 giây")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Không tải được TikTok.\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
            asyncio.create_task(auto_delete(waiting_msg))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        await waiting_msg.delete()
        if data.get("hdplay") or data.get("play"):
            msg = await update.message.reply_video(data.get("hdplay") or data.get("play"),
                                                   caption=f"🎬 {title}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
            asyncio.create_task(auto_delete(msg))
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
                asyncio.create_task(auto_delete(msg))
        else:
            msg = await update.message.reply_text("⚠️ Không tìm thấy video/ảnh.\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
            asyncio.create_task(auto_delete(msg))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok: {e}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(waiting_msg))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /tiktokinfo <username>\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy info @{username}... Tin nhắn này sẽ tự động xoá sau 30 giây")
    try:
        api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
        user = requests.get(api_url, headers=HEADERS, timeout=15).json().get("data", {})
        caption = (
            f"📱 TikTok @{user.get('unique_id', username)}\n"
            f"👤 {user.get('nickname','N/A')}\n"
            f"🌍 Quốc gia: {user.get('region','?')}\n"
            f"👥 Followers: {user.get('follower_count','?')}\n"
            f"❤️ Likes: {user.get('total_favorited','?')}\n"
            f"🎬 Video: {user.get('aweme_count','?')}\n"
            f"📝 Bio: {user.get('signature','')}\n"
            f"⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
        )
        avatar = user.get("avatar")
        await waiting_msg.delete()
        if avatar:
            msg = await update.message.reply_photo(avatar, caption=caption)
        else:
            msg = await update.message.reply_text(caption)
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok info: {e}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(waiting_msg))

# =======================
# MAIN
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
    app.add_handler(CommandHandler("tiktokinfo", tiktok_info))

    # Admin
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()