# bot.py
from telegram import Update, ReplyKeyboardMarkup, ChatMember, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler, MessageHandler, filters
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
    try:
        await asyncio.sleep(delay)
        await msg.delete()
    except:
        pass

# =======================
# 🔧 AI MODE
# =======================
MAINT_MSG = (
    "🛠 *Chức năng AI đang bảo trì*\n\n"
    "Các model ChatGPT, Grok, Gemini tạm thời không hoạt động.\n"
    "📌 Bạn vẫn có thể dùng: /ip, /tiktok, /tiktokinfo."
)

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text("✅ Đã thoát AI\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

# =======================
# 🔒 Admin commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("🛑 Bot đang tắt...\n⏳ Tin nhắn tự xoá sau 30s")
    asyncio.create_task(auto_delete(msg))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("♻️ Bot đang khởi động lại...\n⏳ Tin nhắn tự xoá sau 30s")
    asyncio.create_task(auto_delete(msg))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("✅ Bot đang chạy bình thường!\n⏳ Tin nhắn tự xoá sau 30s")
    asyncio.create_task(auto_delete(msg))

# ==== Kick / Ban / Mute / Unmute ====
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Chỉ admin mới dùng được\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    if not context.args:
        msg = await update.message.reply_text("⚠️ Dùng: /kick @username\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    user = context.args[0].replace("@", "")
    try:
        await update.effective_chat.kick_member(user)
        msg = await update.message.reply_text(f"✅ Đã kick {user}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ Lỗi kick: {e}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Chỉ admin mới dùng được\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    if not context.args:
        msg = await update.message.reply_text("⚠️ Dùng: /ban @username\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    user = context.args[0].replace("@", "")
    try:
        await update.effective_chat.ban_member(user)
        msg = await update.message.reply_text(f"✅ Đã ban {user} vĩnh viễn\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ Lỗi ban: {e}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Chỉ admin mới dùng được\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    if len(context.args)<2:
        msg = await update.message.reply_text("⚠️ Dùng: /mute @username 10m\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    user = context.args[0].replace("@", "")
    duration = context.args[1]
    try:
        from datetime import timedelta
        num, unit = int(duration[:-1]), duration[-1]
        if unit=="m":
            until = timedelta(minutes=num)
        elif unit=="h":
            until = timedelta(hours=num)
        else:
            until = timedelta(minutes=num)
        await update.effective_chat.restrict_member(user, permissions=ChatPermissions(can_send_messages=False), until_date=None)
        msg = await update.message.reply_text(f"✅ Đã khoá mồm {user} trong {duration}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ Lỗi mute: {e}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Chỉ admin mới dùng được\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    if not context.args:
        msg = await update.message.reply_text("⚠️ Dùng: /unmute @username\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
        return
    user = context.args[0].replace("@", "")
    try:
        await update.effective_chat.restrict_member(user, permissions=ChatPermissions(can_send_messages=True))
        msg = await update.message.reply_text(f"✅ Đã mở khoá mồm {user}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ Lỗi unmute: {e}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg))

# =======================
# 🚀 Start / Help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    keyboard = [["/help", "/kick", "/ban", "/mute", "/unmute"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    msg = await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "⚡ Bot cập nhật hằng ngày, ổn định và chuyên nghiệp.\n"
        "📌 Phát triển bởi: Tô Minh Điềm – @DuRinn_LeTuanDiem\n"
        "💡 Gõ /help để xem hướng dẫn chi tiết.\n\n"
        "⏳ Tin nhắn này sẽ tự động xoá sau 30 giây",
        reply_markup=reply_markup
    )
    asyncio.create_task(auto_delete(msg))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    keyboard = [["/start", "/kick", "/ban"], ["/mute", "/unmute"], ["/ip", "/tiktok"], ["/tiktokinfo"], ["/ai", "/gpt", "/grok", "/gemini", "/exit"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = (
        "📖 *Hướng dẫn sử dụng BOT* (chi tiết)\n\n"
        "🚀 Lệnh cơ bản:\n"
        "  • /start — Giới thiệu bot.\n"
        "  • /help — Hiển thị hướng dẫn chi tiết.\n\n"
        "🌐 Công cụ IP:\n"
        "  • /ip <ip> — Xem thông tin IP.\n\n"
        "🎬 Công cụ TikTok:\n"
        "  • /tiktok <link> — Tải video/ảnh TikTok.\n"
        "  • /tiktokinfo <username> — Lấy info TikTok.\n\n"
        "🤖 Chế độ AI (bảo trì):\n"
        "  • /ai, /gpt, /grok, /gemini, /exit\n\n"
        "🔒 Lệnh Admin:\n"
        "  • /shutdown, /restart, /startbot\n"
        "  • /kick @username — Kick người dùng\n"
        "  • /ban @username — Ban vĩnh viễn\n"
        "  • /mute @username 10m — Khoá mồm\n"
        "  • /unmute @username — Mở khoá mồm\n\n"
        "⏳ Tin nhắn tự xoá sau 30 giây"
    )
    msg = await update.message.reply_text(text, reply_markup=reply_markup)
    asyncio.create_task(auto_delete(msg, 30))

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
        msg = await update.message.reply_text("/ip <ip> để kiểm tra thông tin IP\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg, 30))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        msg = await update.message.reply_photo(flag_url, caption=info + "\n⏳ Tin nhắn tự xoá sau 30s")
    else:
        msg = await update.message.reply_text(info + "\n⏳ Tin nhắn tự xoá sau 30s")
    asyncio.create_task(auto_delete(msg, 30))

# =======================
# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("/tiktok <link> để tải video/ảnh TikTok\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg, 30))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Không tải được TikTok\n⏳ Tin nhắn tự xoá sau 30s")
            asyncio.create_task(auto_delete(waiting_msg, 30))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        await waiting_msg.delete()
        if data.get("hdplay") or data.get("play"):
            msg = await update.message.reply_video(
                data.get("hdplay") or data.get("play"),
                caption=f"🎬 {title}\n⏳ Tin nhắn tự xoá sau 30s"
            )
            asyncio.create_task(auto_delete(msg, 30))
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
                asyncio.create_task(auto_delete(msg, 30))
        else:
            msg = await update.message.reply_text("⚠️ Không tìm thấy video/ảnh\n⏳ Tin nhắn tự xoá sau 30s")
            asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok: {e}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(waiting_msg, 30))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("/tiktokinfo <username> để lấy info TikTok\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(msg, 30))
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
            f"📝 Bio: {user.get('signature','')}\n"
            f"⏳ Tin nhắn tự xoá sau 30s"
        )
        avatar = user.get("avatar")
        await waiting_msg.delete()
        if avatar:
            msg = await update.message.reply_photo(avatar, caption=caption)
        else:
            msg = await update.message.reply_text(caption)
        asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok info: {e}\n⏳ Tin nhắn tự xoá sau 30s")
        asyncio.create_task(auto_delete(waiting_msg, 30))

# =======================
# 🎉 Chào người mới
# =======================
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member
    new_user = chat_member.new_chat_member.user
    if chat_member.old_chat_member.status in ["left", "kicked"] and chat_member.new_chat_member.status == "member":
        keyboard = [["/start"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"✨ Chào mừng {new_user.mention_html()} đến với nhóm! ✨\n\n"
                "💡 Gõ /start để xem hướng dẫn và sử dụng BOT Telegram.\n"
                "📌 Bot ổn định, cập nhật hàng ngày, phát triển bởi @DuRinn_LeTuanDiem"
            ),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        asyncio.create_task(auto_delete(msg, 60))

# =======================
# ❌ Xoá tất cả tin nhắn người dùng
# =======================
async def delete_all_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(TOKEN).build()

    # ChatMember handler cho người mới
    app.add_handler(ChatMemberHandler(welcome_new_member, ChatMemberHandler.CHAT_MEMBER))

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
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))

    # Xoá tin nhắn người dùng
    app.add_handler(MessageHandler(filters.ALL, delete_all_user_messages))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()