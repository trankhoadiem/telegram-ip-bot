# bot.py
from telegram import Update, ReplyKeyboardMarkup, ChatMember, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
import requests, os, sys, asyncio
from datetime import datetime, timedelta

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
        "✨ Chào mừng bạn đến với BOT ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini)\n\n"
        "⚡ Bot vẫn đang cập nhật hằng ngày, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @TraMy_2011\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng.\n\n"
        "⏳ Tin nhắn này sẽ tự động xoá sau 30 giây",
        reply_markup=reply_markup
    )
    asyncio.create_task(auto_delete(msg))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    keyboard = [["/start"], ["/ip", "/tiktok"], ["/tiktokinfo"], ["/ai", "/gpt", "/grok", "/gemini", "/exit"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = (
        "📖 Hướng dẫn sử dụng BOT chi tiết 📖\n\n"
        "✨ Bot hỗ trợ nhiều tính năng tiện ích và AI thông minh:\n\n"
        "🔹 /start – Giới thiệu bot và thông tin cơ bản.\n"
        "🔹 /help – Hiển thị danh sách lệnh kèm mô tả chi tiết.\n\n"
        "🤖 Chế độ AI:\n"
        "• /ai – Bật chế độ AI và chọn model để trò chuyện.\n"
        "• /gpt – Dùng ChatGPT Plus – GPT-5, hỗ trợ hỏi đáp thông minh.\n"
        "• /grok – Dùng Grok (xAI), phong cách khác biệt hơn.\n"
        "• /gemini – Dùng Gemini (Google), phản hồi nhanh và súc tích.\n"
        "• /exit – Thoát khỏi chế độ AI.\n"
        "• /ask <câu hỏi> – Lệnh gọi nhanh ChatGPT Plus – GPT-5.\n"
        "👉 Ví dụ: /ask Viết cho tôi một đoạn giới thiệu về công nghệ AI\n\n"
        "🌐 Công cụ khác:\n"
        "• /ip <ip> – Kiểm tra thông tin chi tiết của một địa chỉ IP.\n"
        "• /tiktok <link> – Tải video/ảnh TikTok không watermark.\n"
        "• /testapi – Kiểm tra trạng thái các API key (GPT, Grok, Gemini).\n\n"
        "🔒 Lệnh Admin:\n"
        "• /shutdown – Tắt bot.\n"
        "• /restart – Khởi động lại bot.\n"
        "• /startbot – Kiểm tra bot đang chạy.\n"
        "• /mute – 🔒 Khóa chat.\n"
        "• /unmute – 🔓 Mở chat.\n"
        "• /kick – Đuổi thành viên ra khỏi nhóm.\n"
        "• /ban – Cấm thành viên.\n\n"
        "💡 Lưu ý: Một số lệnh yêu cầu bạn phải nhập đúng cú pháp để bot hiểu.\n"
        "👉 Hãy thử ngay bằng cách gõ /ask và đặt câu hỏi cho ChatGPT Plus – GPT-5!\n\n"
        "✨ ChatGPT Plus – GPT-5\n"
        "by @DuRinn_LeTuanDiem\n\n"
        "⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
    )
    msg = await update.message.reply_text(text, reply_markup=reply_markup)
    asyncio.create_task(auto_delete(msg, 30))

# =======================
# 🎉 Chào người mới
# =======================
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member
    new_user = chat_member.new_chat_member.user

    if chat_member.old_chat_member.status in ["left", "kicked"] and chat_member.new_chat_member.status == "member":
        keyboard = [["/start", "/help"], ["/ai", "/gpt", "/grok", "/gemini", "/exit"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"✨ Chào mừng {new_user.mention_html()} đến với nhóm! ✨\n\n"
                "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini)\n\n"
                "⚡ Bot vẫn đang cập nhật hằng ngày, có thể tồn tại một số lỗi.\n\n"
                "📌 Thành viên phát triển BOT:\n"
                "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
                "   👤 Telegram Support – @TraMy_2011\n"
                "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
                "💡 Gõ /help để xem tất cả lệnh khả dụng."
            ),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        asyncio.create_task(auto_delete(msg, 60))

# =======================
# 🌐 IP checker
# =======================
async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("❌ Vui lòng nhập địa chỉ IP.\n👉 Ví dụ: /ip 8.8.8.8")
        asyncio.create_task(auto_delete(msg))
        return
    ip = context.args[0]
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        if res["status"] == "fail":
            msg = await update.message.reply_text("❌ Không tìm thấy thông tin IP này.")
            asyncio.create_task(auto_delete(msg))
            return
        text = (
            f"🌐 Thông tin IP: `{ip}`\n\n"
            f"🏙 Thành phố: {res.get('city','N/A')}\n"
            f"🌍 Quốc gia: {res.get('country','N/A')}\n"
            f"📡 ISP: {res.get('isp','N/A')}\n"
            f"🗺 Vĩ độ: {res.get('lat','N/A')}\n"
            f"🗺 Kinh độ: {res.get('lon','N/A')}\n"
        )
        msg = await update.message.reply_text(text, parse_mode="Markdown")
        asyncio.create_task(auto_delete(msg, 30))
    except Exception:
        msg = await update.message.reply_text("⚠️ Lỗi khi tra cứu IP.")
        asyncio.create_task(auto_delete(msg))

# =======================
# 🎬 TikTok Downloader
# =======================
async def tiktok_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("❌ Vui lòng nhập link TikTok.\n👉 Ví dụ: /tiktok <link>")
        asyncio.create_task(auto_delete(msg))
        return
    url = context.args[0]
    try:
        res = requests.post(f"{TIKWM_API}download", headers=HEADERS, data={"url": url}).json()
        if res["code"] != 0:
            msg = await update.message.reply_text("❌ Không thể tải video TikTok.")
            asyncio.create_task(auto_delete(msg))
            return
        video_url = "https://www.tikwm.com" + res["data"]["play"]
        await update.message.reply_video(video_url, caption="🎬 Video TikTok không watermark")
    except Exception:
        msg = await update.message.reply_text("⚠️ Lỗi khi tải video TikTok.")
        asyncio.create_task(auto_delete(msg))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("❌ Vui lòng nhập link TikTok.\n👉 Ví dụ: /tiktokinfo <link>")
        asyncio.create_task(auto_delete(msg))
        return
    url = context.args[0]
    try:
        res = requests.post(f"{TIKWM_API}detail", headers=HEADERS, data={"url": url}).json()
        if res["code"] != 0:
            msg = await update.message.reply_text("❌ Không thể lấy thông tin video TikTok.")
            asyncio.create_task(auto_delete(msg))
            return
        data = res["data"]
        text = (
            f"🎬 Thông tin video TikTok\n\n"
            f"👤 Tác giả: {data['author']['unique_id']}\n"
            f"❤️ Lượt thích: {data['digg_count']}\n"
            f"💬 Bình luận: {data['comment_count']}\n"
            f"🔄 Chia sẻ: {data['share_count']}\n"
            f"👀 Lượt xem: {data['play_count']}"
        )
        msg = await update.message.reply_text(text)
        asyncio.create_task(auto_delete(msg, 30))
    except Exception:
        msg = await update.message.reply_text("⚠️ Lỗi khi lấy thông tin TikTok.")
        asyncio.create_task(auto_delete(msg))

# =======================
# 🔨 Moderation
# =======================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền.")
        asyncio.create_task(auto_delete(msg))
        return
    chat_id = update.effective_chat.id
    await context.bot.set_chat_permissions(chat_id, ChatPermissions(can_send_messages=False))
    msg = await update.message.reply_text("🔒 Nhóm đã bị khóa chat.")
    asyncio.create_task(auto_delete(msg))

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền.")
        asyncio.create_task(auto_delete(msg))
        return
    chat_id = update.effective_chat.id
    await context.bot.set_chat_permissions(chat_id, ChatPermissions(can_send_messages=True))
    msg = await update.message.reply_text("🔓 Nhóm đã được mở chat.")
    asyncio.create_task(auto_delete(msg))

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update) or not update.message.reply_to_message:
        msg = await update.message.reply_text("⛔ Bạn không có quyền hoặc không reply user.")
        asyncio.create_task(auto_delete(msg))
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user_id, until_date=datetime.now() + timedelta(seconds=60))
    await context.bot.unban_chat_member(update.effective_chat.id, user_id)
    msg = await update.message.reply_text("👢 Thành viên đã bị kick.")
    asyncio.create_task(auto_delete(msg))

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update) or not update.message.reply_to_message:
        msg = await update.message.reply_text("⛔ Bạn không có quyền hoặc không reply user.")
        asyncio.create_task(auto_delete(msg))
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user_id)
    msg = await update.message.reply_text("⛔ Thành viên đã bị ban.")
    asyncio.create_task(auto_delete(msg))

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
    app.add_handler(CommandHandler("ip", ip_lookup))
    app.add_handler(CommandHandler("tiktok", tiktok_download))
    app.add_handler(CommandHandler("tiktokinfo", tiktok_info))

    # Admin
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
