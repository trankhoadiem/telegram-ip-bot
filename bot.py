# bot.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
import requests, os, asyncio, sys

# ====== TOKEN ======
TOKEN = os.environ.get("TOKEN")
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

# ====== ADMIN CHECK ======
def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ====== TikTok API ======
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

# ====== HELPER ======
async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except:
        pass

async def send_temp_message(update: Update, text: str, delay: int = 15, reply_markup=None):
    msg = await update.message.reply_text(
        text + f"\n\n⏳ (Tin nhắn này sẽ tự động xoá sau {delay} giây)",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# ====== AI MODE ======
MAINT_MSG = (
    "🛠 *Chức năng AI đang bảo trì & nâng cấp*\n\n"
    "Các model AI như ChatGPT, Grok, Gemini tạm thời không hoạt động.\n\n"
    "📌 Bạn vẫn có thể sử dụng các công cụ: /ip, /tiktok, /tiktokinfo."
)

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG)
    asyncio.create_task(auto_delete(msg))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text("✅ Bạn đã thoát khỏi chế độ AI.")
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

# ====== ADMIN COMMANDS ======
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("🛑 Bot đang tắt...")
    asyncio.create_task(auto_delete(msg))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("♻️ Bot đang khởi động lại...")
    asyncio.create_task(auto_delete(msg))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("❌ Bạn không có quyền dùng lệnh này.")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("✅ Bot đang hoạt động bình thường.")
    asyncio.create_task(auto_delete(msg))

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    keyboard = [
        [InlineKeyboardButton("📖 Hướng dẫn", callback_data="help")],
        [InlineKeyboardButton("🌐 Tra IP", callback_data="ip")],
        [InlineKeyboardButton("🎬 TikTok", callback_data="tiktok")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "🚀 **Chào mừng bạn đến với BOT**\n\n"
        "⚡ Bot liên tục **cập nhật và tối ưu** để mang lại trải nghiệm tốt nhất.\n\n"
        "📌 *Nhóm phát triển*:\n"
        "   👤 Tô Minh Điềm – @DuRinn_LeTuanDiem\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n"
        "   🆘 Hỗ trợ – @Telegram\n\n"
        "💡 Gõ /help để xem tất cả lệnh và hướng dẫn chi tiết."
    )
    await send_temp_message(update, text, 15, reply_markup)

# ====== HELP ======
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    text = (
        "📖 *Hướng dẫn sử dụng BOT Pro*\n\n"

        "🚀 **Lệnh cơ bản**:\n"
        "   • /start — Hiển thị thông tin giới thiệu bot.\n"
        "   • /help — Hiển thị hướng dẫn chi tiết các lệnh.\n\n"

        "🤖 **Chế độ AI** (🛠 đang bảo trì):\n"
        "   • /ai — Bật chế độ AI.\n"
        "   • /gpt — ChatGPT.\n"
        "   • /grok — Grok.\n"
        "   • /gemini — Gemini.\n"
        "   • /exit — Thoát chế độ AI.\n\n"

        "🌐 **Công cụ IP**:\n"
        "   • /ip <ip> — Kiểm tra thông tin chi tiết của một IP.\n"
        "     💡 Ví dụ: /ip 8.8.8.8\n\n"

        "🎬 **Công cụ TikTok**:\n"
        "   • /tiktok <link> — Tải video hoặc ảnh TikTok.\n"
        "   • /tiktokinfo <username> — Lấy thông tin tài khoản TikTok: tên, UID, quốc gia, followers, likes, bio...\n"
        "     💡 Ví dụ: /tiktokinfo username\n\n"

        "🔒 **Lệnh Admin (chỉ @DuRinn_LeTuanDiem)**:\n"
        "   • /shutdown — Tắt bot.\n"
        "   • /restart — Khởi động lại bot.\n"
        "   • /startbot — Kiểm tra bot hoạt động.\n\n"

        "⚡ *Bot được tối ưu và cập nhật liên tục.*"
    )
    await send_temp_message(update, text, 30)

# ====== IP CHECK ======
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy IP: {ip}"
        info = (
            f"🌐 IP: {res['query']}\n"
            f"🏳️ Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Thành phố: {res['regionName']} - {res['city']}\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📍 Tọa độ: {res['lat']}, {res['lon']}\n"
            f"📡 ISP: {res['isp']}\n"
            f"🏢 Tổ chức: {res['org']}\n"
            f"🔗 AS: {res['as']}"
        )
        return f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png", info
    except:
        return None, f"⚠️ Lỗi IP"

async def check_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /ip <địa_chỉ_ip>")
        asyncio.create_task(auto_delete(msg))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        msg = await update.message.reply_photo(flag_url, caption=info)
    else:
        msg = await update.message.reply_text(info)
    asyncio.create_task(auto_delete(msg))

# ====== TikTok ======
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /tiktok <link>")
        asyncio.create_task(auto_delete(msg))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Không tải được TikTok.")
            asyncio.create_task(auto_delete(waiting_msg))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        await waiting_msg.delete()
        if data.get("hdplay") or data.get("play"):
            msg = await update.message.reply_video(data.get("hdplay") or data.get("play"),
                                                   caption=f"🎬 {title}")
            asyncio.create_task(auto_delete(msg))
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
                asyncio.create_task(auto_delete(msg))
        else:
            msg = await update.message.reply_text("⚠️ Không tìm thấy video/ảnh.")
            asyncio.create_task(auto_delete(msg))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok: {e}")
        asyncio.create_task(auto_delete(waiting_msg))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Dùng: /tiktokinfo <username>")
        asyncio.create_task(auto_delete(msg))
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy info @{username}...")
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
            f"📝 Bio: {user.get('signature','')}"
        )
        avatar = user.get("avatar")
        await waiting_msg.delete()
        if avatar:
            msg = await update.message.reply_photo(avatar, caption=caption)
        else:
            msg = await update.message.reply_text(caption)
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok info: {e}")
        asyncio.create_task(auto_delete(waiting_msg))

# ====== AUTO DELETE ======
async def auto_delete(msg, delay=15):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# ====== MAIN ======
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

    print("🤖 Bot Pro đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()