# bot.py
from telegram import Update, ReplyKeyboardMarkup, ChatMember, ChatPermissions, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
import requests, os, sys, asyncio
from datetime import datetime, timedelta
from io import BytesIO

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
# 🌐 IP Checker
# =======================
async def ip_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("⚠️ Vui lòng nhập IP. Ví dụ: /ip 8.8.8.8")
        asyncio.create_task(auto_delete(msg))
        return

    ip = context.args[0]
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,lat,lon,isp,org,query").json()
        if res["status"] != "success":
            raise Exception(res.get("message", "Không tìm thấy IP"))

        text = (
            f"🌍 Thông tin IP: {res['query']}\n"
            f"📌 Quốc gia: {res['country']}\n"
            f"🏙 Thành phố: {res['city']}, {res['regionName']}\n"
            f"🌐 ISP: {res['isp']}\n"
            f"🏢 Tổ chức: {res['org']}\n"
            f"📍 Tọa độ: {res['lat']}, {res['lon']}"
        )

        map_url = f"https://maps.locationiq.com/v3/staticmap?key=pk.eyJ1IjoiZHVyaW5uIiwiYSI6ImNseW92c2hrZzA0MGMyaXFsaXR5MWJwMmYifQ.abc123&center={res['lat']},{res['lon']}&zoom=10&size=600x400&markers=icon:small-red-cutout|{res['lat']},{res['lon']}"
        map_img = requests.get(map_url).content

        msg = await update.message.reply_photo(photo=BytesIO(map_img), caption=text)
        asyncio.create_task(auto_delete(msg, 60))

    except Exception as e:
        msg = await update.message.reply_text(f"❌ Lỗi: {e}")
        asyncio.create_task(auto_delete(msg))

# =======================
# 🎬 TikTok Downloader
# =======================
async def tiktok_dl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("⚠️ Vui lòng nhập link TikTok. Ví dụ: /tiktok <link>")
        asyncio.create_task(auto_delete(msg))
        return

    url = context.args[0]
    try:
        res = requests.post(TIKWM_API, headers=HEADERS, data={"url": url}).json()
        if res["code"] != 0:
            raise Exception(res.get("msg", "API lỗi"))

        data = res["data"]
        video_url = "https://www.tikwm.com" + data["play"]
        caption = f"🎬 Video từ TikTok\n\n👤 Tác giả: {data['author']['unique_id']}\n❤️ {data['digg_count']} | 💬 {data['comment_count']} | 🔁 {data['share_count']}"

        msg = await update.message.reply_video(video=video_url, caption=caption)
        asyncio.create_task(auto_delete(msg, 120))

    except Exception as e:
        msg = await update.message.reply_text(f"❌ Lỗi tải TikTok: {e}")
        asyncio.create_task(auto_delete(msg))

# =======================
# 🔨 Moderation
# =======================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not update.message.reply_to_message:
        msg = await update.message.reply_text("⚠️ Hãy reply tin nhắn của người cần mute.")
        asyncio.create_task(auto_delete(msg))
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.restrict_chat_member(update.effective_chat.id, user_id, ChatPermissions(can_send_messages=False))
    msg = await update.message.reply_text("🔒 Người dùng đã bị mute.")
    asyncio.create_task(auto_delete(msg))

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not update.message.reply_to_message:
        msg = await update.message.reply_text("⚠️ Hãy reply tin nhắn của người cần unmute.")
        asyncio.create_task(auto_delete(msg))
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.restrict_chat_member(update.effective_chat.id, user_id, ChatPermissions(can_send_messages=True))
    msg = await update.message.reply_text("🔓 Người dùng đã được unmute.")
    asyncio.create_task(auto_delete(msg))

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not update.message.reply_to_message:
        msg = await update.message.reply_text("⚠️ Hãy reply tin nhắn của người cần kick.")
        asyncio.create_task(auto_delete(msg))
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user_id, until_date=datetime.now() + timedelta(seconds=60))
    msg = await update.message.reply_text("👢 Người dùng đã bị kick.")
    asyncio.create_task(auto_delete(msg))

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not update.message.reply_to_message:
        msg = await update.message.reply_text("⚠️ Hãy reply tin nhắn của người cần ban.")
        asyncio.create_task(auto_delete(msg))
        return
    user_id = update.message.reply_to_message.from_user.id
    await context.bot.ban_chat_member(update.effective_chat.id, user_id)
    msg = await update.message.reply_text("⛔ Người dùng đã bị ban.")
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
    app.add_handler(CommandHandler("tiktok", tiktok_dl))

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
