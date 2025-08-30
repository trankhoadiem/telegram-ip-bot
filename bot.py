# bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
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

async def auto_delete(msg, delay=15):
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
    "⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây"
)

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg, 15))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text("✅ Đã thoát khỏi chế độ AI.\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
    asyncio.create_task(auto_delete(msg, 15))

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg, 15))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg, 15))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg, 15))

# =======================
# 🔒 Admin commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
        asyncio.create_task(auto_delete(msg, 15))
        return
    msg = await update.message.reply_text("🛑 Bot đang tắt...\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
    asyncio.create_task(auto_delete(msg, 15))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
        asyncio.create_task(auto_delete(msg, 15))
        return
    msg = await update.message.reply_text("♻️ Bot đang khởi động lại...\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
    asyncio.create_task(auto_delete(msg, 15))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
        asyncio.create_task(auto_delete(msg, 15))
        return
    msg = await update.message.reply_text("✅ Bot đang chạy bình thường!\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
    asyncio.create_task(auto_delete(msg, 15))

# =======================
# 🚀 Start / Help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    keyboard = [[InlineKeyboardButton("📖 Hướng dẫn", callback_data="help")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT Pro** ✨\n\n"
        "⚡ Bot liên tục được cập nhật hằng ngày, trải nghiệm mượt mà & chuyên nghiệp.\n\n"
        "📌 **Developer:** 👤 Tô Minh Điềm – @DuRinn_LeTuanDiem\n"
        "💡 Bấm nút 'Hướng dẫn' để xem chi tiết các lệnh.\n"
        "⚠️ Tin nhắn này sẽ tự động xoá sau 10 giây",
        reply_markup=reply_markup
    )
    asyncio.create_task(auto_delete(msg, 10))  # 10 giây

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    text = (
        "📖 **Hướng dẫn sử dụng BOT Pro** 📖\n\n"
        "🚀 **Lệnh cơ bản**:\n"
        "   • /start — Hiển thị giới thiệu BOT.\n"
        "   • /help — Xem hướng dẫn chi tiết.\n\n"
        "🤖 **Chế độ AI** (🔧 đang bảo trì):\n"
        "   • /ai — Bật chế độ AI.\n"
        "   • /gpt — ChatGPT.\n"
        "   • /grok — Grok.\n"
        "   • /gemini — Gemini.\n"
        "   • /exit — Thoát chế độ AI.\n\n"
        "🌐 **Công cụ IP**:\n"
        "   • /ip <ip> — Kiểm tra thông tin chi tiết IP.\n"
        "     💡 Ví dụ: /ip 8.8.8.8\n\n"
        "🎬 **Công cụ TikTok**:\n"
        "   • /tiktok <link> — Tải video hoặc ảnh TikTok.\n"
        "   • /tiktokinfo <username> — Lấy info tài khoản TikTok.\n\n"
        "🔒 **Admin (chỉ @DuRinn_LeTuanDiem)**:\n"
        "   • /shutdown — Tắt bot.\n"
        "   • /restart — Khởi động lại bot.\n"
        "   • /startbot — Kiểm tra bot.\n\n"
        "⚡ Bot được phát triển & cập nhật liên tục.\n"
        "⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây"
    )
    msg = await update.message.reply_text(text)
    asyncio.create_task(auto_delete(msg, 15))  # 15 giây

# Callback button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "help":
        await help_command(update, context)

# =======================
# 🌐 IP checker
# =======================
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy IP: {ip}\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây"
        info = (
            f"🌐 Thông tin IP {res['query']}:\n"
            f"🏳️ Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Thành phố: {res['regionName']} - {res['city']} ({res.get('zip','')})\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📍 Tọa độ: {res['lat']}, {res['lon']}\n"
            f"📡 ISP: {res['isp']}\n"
            f"🏢 Tổ chức: {res['org']}\n"
            f"🔗 AS: {res['as']}\n"
            f"⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây"
        )
        return f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png", info
    except Exception as e:
        return None, f"⚠️ Lỗi IP: {e}\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây"

async def check_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /ip <địa_chỉ_ip>\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
        asyncio.create_task(auto_delete(msg, 15))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        msg = await update.message.reply_photo(flag_url, caption=info)
    else:
        msg = await update.message.reply_text(info)
    asyncio.create_task(auto_delete(msg, 15))

# =======================
# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /tiktok <link>\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
        asyncio.create_task(auto_delete(msg, 15))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok...\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Không tải được TikTok.\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
            asyncio.create_task(auto_delete(waiting_msg, 15))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        await waiting_msg.delete()
        if data.get("hdplay") or data.get("play"):
            msg = await update.message.reply_video(data.get("hdplay") or data.get("play"),
                                                   caption=f"🎬 {title}\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
            asyncio.create_task(auto_delete(msg, 15))
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
                asyncio.create_task(auto_delete(msg, 15))
        else:
            msg = await update.message.reply_text("⚠️ Không tìm thấy video/ảnh.\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
            asyncio.create_task(auto_delete(msg, 15))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok: {e}\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
        asyncio.create_task(auto_delete(waiting_msg, 15))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /tiktokinfo <username>\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
        asyncio.create_task(auto_delete(msg, 15))
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy info @{username}...\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
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
            f"⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây"
        )
        avatar = user.get("avatar")
        await waiting_msg.delete()
        if avatar:
            msg = await update.message.reply_photo(avatar, caption=caption)
        else:
            msg = await update.message.reply_text(caption)
        asyncio.create_task(auto_delete(msg, 15))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok info: {e}\n⚠️ Tin nhắn này sẽ tự động xoá sau 15 giây")
        asyncio.create_task(auto_delete(waiting_msg, 15))

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

    # Button callback
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()