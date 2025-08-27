from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os

TOKEN = os.environ.get("TOKEN")   # Token bot Telegram (set trên Railway)

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ tra cứu IP & tải TikTok video/ảnh chất lượng cao.\n\n"
        "📌 Các thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/tiktok <link> - Tải video/ảnh TikTok"
    )

# ==== Check IP ====
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url).json()

        if res["status"] == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"

        info = (
            f"🌍 Thông tin IP {res['query']}:\n"
            f"🗺 Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Khu vực: {res['regionName']} - {res['city']} ({res['zip']})\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📍 Toạ độ: {res['lat']}, {res['lon']}\n"
            f"📡 ISP: {res['isp']}\n"
            f"🏢 Tổ chức: {res['org']}\n"
            f"🔗 AS: {res['as']}"
        )
        flag_url = f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png"
        return flag_url, info
    except Exception as e:
        return None, f"⚠️ Lỗi khi kiểm tra IP: {e}"

async def check_ip(update, context):
    # Xoá tin nhắn user sau khi nhập lệnh
    try:
        await update.message.delete()
    except:
        pass

    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0]
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=info)
    else:
        await update.message.reply_text(info)

# ==== Download TikTok ====
async def download_tiktok(update, context):
    # Xoá tin nhắn user sau khi nhập lệnh
    try:
        await update.message.delete()
    except:
        pass

    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link video TikTok>")
        return

    link = context.args[0]

    # Gửi thông báo đang xử lý
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok, vui lòng chờ...")

    try:
        api = "https://www.tikwm.com/api/"
        res = requests.post(api, data={"url": link}).json()

        if res.get("code") != 0:
            await waiting_msg.edit_text("❌ Không tải được TikTok. Kiểm tra lại link!")
            return

        data = res["data"]
        title = data.get("title", "TikTok video")

        # Nếu là video
        if "play" in data:
            keyboard = [
                [InlineKeyboardButton("📹 480p", callback_data=f"480|{data['play']}")],
                [InlineKeyboardButton("📹 1080p", callback_data=f"1080|{data['hdplay']}")],
                [InlineKeyboardButton("🎵 Audio (MP3)", callback_data=f"audio|{data['music']}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await waiting_msg.edit_text(
                f"🎬 {title}\n\nChọn chất lượng tải:",
                reply_markup=reply_markup
            )

        # Nếu là ảnh
        elif "images" in data:
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh gốc...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)

    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== Handle chọn chất lượng ====
async def button(update, context):
    query = update.callback_query
    await query.answer()

    try:
        quality, url = query.data.split("|", 1)
        if quality == "audio":
            await query.message.reply_audio(url, caption="🎵 Nhạc gốc TikTok")
        else:
            await query.message.reply_video(url, caption=f"🎬 Video TikTok {quality}")
    except Exception as e:
        await query.message.reply_text(f"⚠️ Lỗi khi gửi video: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
