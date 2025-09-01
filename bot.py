import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Hàm xử lý lệnh /ip
async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        msg = await update.message.reply_text("Vui lòng cung cấp một địa chỉ IP.\nVí dụ: /ip 8.8.8.8")
        return

    ip_address = context.args[0]
    url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    res = requests.get(url, timeout=15).json()

    if res.get("status") == "fail":
        await update.message.reply_text(f"❌ Không tìm thấy IP: {ip_address}")
        return

    info = (
        f"🌐 Thông tin IP {res['query']}:\n"
        f"🏳️ Quốc gia: {res['country']} ({res['countryCode']})\n"
        f"🏙 Thành phố: {res['regionName']} - {res['city']} ({res.get('zip', '')})\n"
        f"🕒 Múi giờ: {res['timezone']}\n"
        f"📍 Tọa độ: {res['lat']}, {res['lon']}\n"
        f"📡 ISP: {res['isp']}\n"
        f"🏢 Tổ chức: {res['org']}\n"
        f"🔗 AS: {res['as']}"
    )
    await update.message.reply_text(info, reply_markup=None)

# Hàm xử lý lệnh /tiktok
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            msg = await update.message.reply_video(data.get("hdplay") or data.get("play"), caption=f"🎬 {title}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
            asyncio.create_task(auto_delete(msg, 30))
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
                asyncio.create_task(auto_delete(msg, 30))
        else:
            await update.message.reply_text("❌ Không có video hoặc ảnh từ link TikTok này.")
    except Exception as e:
        await waiting_msg.edit_text(f"❌ Lỗi: {str(e)}")

# Hàm xóa tin nhắn tự động sau 30 giây
async def auto_delete(msg, seconds):
    await asyncio.sleep(seconds)
    await msg.delete()

# Hàm xử lý các lệnh Admin
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Tắt bot...")
    # Tắt bot tại đây (dừng tất cả process)
    await application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Đang khởi động lại bot...")
    # Khởi động lại bot tại đây
    await application.stop()

# Cấu hình lệnh admin
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Vui lòng cung cấp ID người dùng để kick.")
        return
    user_id = context.args[0]
    try:
        await update.message.chat.kick_member(user_id)
        await update.message.reply_text(f"Đã đuổi thành viên {user_id} khỏi nhóm.")
    except Exception as e:
        await update.message.reply_text(f"❌ Lỗi: {str(e)}")

# Định nghĩa lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Chào mừng bạn đến với BOT ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini)\n\n"
        "⚡ Bot vẫn đang cập nhật hằng ngày, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @TraMy_2011\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng."
    )

# Cấu hình lệnh /help
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
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
        "• /ban – Cấm thành viên."
    )

# Cấu hình bot
def main():
    application = Application.builder().token("YOUR_BOT_TOKEN").build()

    # Thêm các handler cho các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("ip", ip))
    application.add_handler(CommandHandler("tiktok", download_tiktok))
    application.add_handler(CommandHandler("shutdown", shutdown))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("kick", kick))

    # Khởi chạy bot
    application.run_polling()

if __name__ == "__main__":
    main()
