# bot.py
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio, os, requests

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"
def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# =======================
# 🚀 Start / Help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    keyboard = [["/help", "/kick", "/ban", "/mute", "/unmute"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    msg = await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
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
    await update.message.delete()
    keyboard = [["/start"], ["/ip", "/tiktok"], ["/tiktokinfo"], ["/ai", "/gpt", "/grok", "/gemini", "/exit"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = (
        "📖 *Hướng dẫn sử dụng BOT chi tiết* 📖\n\n"
        "✨ Bot hỗ trợ nhiều tính năng tiện ích và AI thông minh:\n\n"
        "🔹 /start – Giới thiệu bot và thông tin cơ bản.\n"
        "🔹 /help – Hiển thị danh sách lệnh kèm mô tả chi tiết.\n\n"
        "🤖 Chế độ AI:\n"
        "  • /ai – Bật chế độ AI và chọn model để trò chuyện.\n"
        "  • /gpt – Dùng ChatGPT Plus – GPT-5, hỗ trợ hỏi đáp thông minh.\n"
        "  • /grok – Dùng Grok (xAI), phong cách khác biệt hơn.\n"
        "  • /gemini – Dùng Gemini (Google), phản hồi nhanh và súc tích.\n"
        "  • /exit – Thoát khỏi chế độ AI.\n"
        "  • /ask <câu hỏi> – Lệnh gọi nhanh ChatGPT Plus – GPT-5.\n"
        "👉 Ví dụ: /ask Viết cho tôi một đoạn giới thiệu về công nghệ AI\n\n"
        "🌐 Công cụ khác:\n"
        "  • /ip <ip> – Kiểm tra thông tin chi tiết của một địa chỉ IP.\n"
        "  • /tiktok <link> – Tải video/ảnh TikTok không watermark.\n"
        "  • /testapi – Kiểm tra trạng thái các API key (GPT, Grok, Gemini).\n\n"
        "🔒 Lệnh Admin:\n"
        "  • /shutdown – Tắt bot.\n"
        "  • /restart – Khởi động lại bot.\n"
        "  • /startbot – Kiểm tra bot đang chạy.\n"
        "  • /mute – 🔒 Khóa chat.\n"
        "  • /unmute – 🔓 Mở chat.\n"
        "  • /kick – Đuổi thành viên ra khỏi nhóm.\n"
        "  • /ban – Cấm thành viên.\n\n"
        "💡 Lưu ý: Một số lệnh yêu cầu bạn phải nhập đúng cú pháp để bot hiểu.\n"
        "👉 Hãy thử ngay bằng cách gõ /ask và đặt câu hỏi cho ChatGPT Plus – GPT-5!\n\n"
        "✨ ChatGPT Plus – GPT-5\nby @DuRinn_LeTuanDiem\n\n"
        "⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
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
    await update.message.delete()
    if not context.args:
        msg = await update.message.reply_text("/ip <ip> để kiểm tra thông tin IP\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg, 30))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        msg = await update.message.reply_photo(flag_url, caption=info + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    else:
        msg = await update.message.reply_text(info + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg, 30))

# =======================
# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    if not context.args:
        msg = await update.message.reply_text("/tiktok <link> để tải video/ảnh TikTok\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg, 30))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok...")
    try:
        res = requests.post("https://www.tikwm.com/api/", data={"url": link}, headers={"User-Agent": "Mozilla/5.0"}, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Không tải được TikTok\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
            asyncio.create_task(auto_delete(waiting_msg, 30))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        await waiting_msg.delete()
        if data.get("hdplay") or data.get("play"):
            msg = await update.message.reply_video(
                data.get("hdplay") or data.get("play"),
                caption=f"🎬 {title}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
            )
            asyncio.create_task(auto_delete(msg, 30))
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
                asyncio.create_task(auto_delete(msg, 30))
        else:
            msg = await update.message.reply_text("⚠️ Không tìm thấy video/ảnh\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
            asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok: {e}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(waiting_msg, 30))

# =======================
# 🛠️ Helper Function (Auto Delete)
# =======================
async def auto_delete(msg, delay=30):
    await asyncio.sleep(delay)
    await msg.delete()

# =======================
# Run Bot
# =======================
if __name__ == "__main__":
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("ip", check_ip))
    application.add_handler(CommandHandler("tiktok", download_tiktok))

    application.run_polling()
