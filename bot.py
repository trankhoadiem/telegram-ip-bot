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
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("🛑 Bot đang tắt...\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("♻️ Bot đang khởi động lại...\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("✅ Bot đang chạy bình thường!\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
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
    keyboard = [["/start"], ["/ip", "/tiktok"], ["/tiktokinfo"], ["/ai", "/gpt", "/grok", "/gemini", "/exit"], ["/kick", "/ban", "/mute", "/unmute"]]
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
        "  • /shutdown, /restart, /startbot (chỉ admin)\n"
        "  • /kick <username> — Đuổi người dùng\n"
        "  • /ban <username> — Cấm người dùng vĩnh viễn\n"
        "  • /mute <username> <time> — Khoá mõm người dùng (vd: 1m, 1h)\n"
        "  • /unmute <username> — Mở khoá mõm\n\n"
        "⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
    )
    msg = await update.message.reply_text(text, reply_markup=reply_markup)
    asyncio.create_task(auto_delete(msg, 30))

# =======================
# 🎉 Xoá tin nhắn người dùng
# =======================
async def delete_all_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

# =======================
# 🎉 Welcome
# =======================
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member
    new_user = chat_member.new_chat_member.user
    if chat_member.old_chat_member.status in ["left", "kicked"] and chat_member.new_chat_member.status == "member":
        keyboard = [["/start", "/kick", "/ban", "/mute", "/unmute"]]
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
# 🔒 Admin kick/ban/mute/unmute
# =======================
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Chỉ admin mới có thể dùng lệnh này")
        asyncio.create_task(auto_delete(msg))
        return
    if not context.args:
        msg = await update.message.reply_text("❌ /kick <username>")
        asyncio.create_task(auto_delete(msg))
        return
    username = context.args[0].replace("@","")
    chat = update.effective_chat
    member = await chat.get_member(username)
    await chat.kick_member(member.user.id)
    msg = await update.message.reply_text(f"✅ Đã đuổi {member.user.mention_html()} khỏi nhóm (1 phút)")
    asyncio.create_task(auto_delete(msg, 60))

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Chỉ admin mới có thể dùng lệnh này")
        asyncio.create_task(auto_delete(msg))
        return
    if not context.args:
        msg = await update.message.reply_text("❌ /ban <username>")
        asyncio.create_task(auto_delete(msg))
        return
    username = context.args[0].replace("@","")
    chat = update.effective_chat
    member = await chat.get_member(username)
    await chat.ban_member(member.user.id)
    msg = await update.message.reply_text(f"⛔ {member.user.mention_html()} đã bị cấm vĩnh viễn")
    asyncio.create_task(auto_delete(msg, 60))

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Chỉ admin mới có thể dùng lệnh này")
        asyncio.create_task(auto_delete(msg))
        return
    if len(context.args)<2:
        msg = await update.message.reply_text("❌ /mute <username> <time>\nvd: 1m = 1 phút, 1h = 1 giờ")
        asyncio.create_task(auto_delete(msg))
        return
    username = context.args[0].replace("@","")
    time_str = context.args[1]
    seconds = 60 if time_str.endswith("m") else 3600
    chat = update.effective_chat
    member = await chat.get_member(username)
    await chat.restrict_member(member.user.id, permissions=ChatPermissions(can_send_messages=False), until_date=seconds)
    msg = await update.message.reply_text(f"🔇 {member.user.mention_html()} đã bị khoá mõm {time_str}")
    asyncio.create_task(auto_delete(msg, 60))

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Chỉ admin mới có thể dùng lệnh này")
        asyncio.create_task(auto_delete(msg))
        return
    if not context.args:
        msg = await update.message.reply_text("❌ /unmute <username>")
        asyncio.create_task(auto_delete(msg))
        return
    username = context.args[0].replace("@","")
    chat = update.effective_chat
    member = await chat.get_member(username)
    await chat.restrict_member(member.user.id, permissions=ChatPermissions(can_send_messages=True))
    msg = await update.message.reply_text(f"🔊 {member.user.mention_html()} đã được mở khoá mõm")
    asyncio.create_task(auto_delete(msg, 60))

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