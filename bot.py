from telegram.ext import Application, CommandHandler
import requests
import os

TOKEN = os.environ.get("TOKEN")   # Token bot Telegram (set trên Railway)
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")  # API key của YouTube Data API v3

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Đây là công cụ hỗ trợ tra cứu thông tin IP, YouTube, TikTok nhanh chóng và chính xác.\n\n"
        "📌 Bot được phát triển và duy trì bởi đội ngũ:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem các lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/yt <channel_id hoặc username> - Lấy thông tin YouTube\n"
        "/tiktok <username> - Lấy thông tin TikTok"
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
    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0]
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=info)
    else:
        await update.message.reply_text(info)

# ==== Check YouTube ====
async def check_yt(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /yt <channel_id hoặc username>")
        return

    channel_id = context.args[0]

    try:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={YOUTUBE_API_KEY}"
        res = requests.get(url).json()

        if "items" not in res or not res["items"]:
            await update.message.reply_text("❌ Không tìm thấy kênh YouTube này.")
            return

        data = res["items"][0]
        snippet = data["snippet"]
        stats = data["statistics"]

        msg = (
            f"📺 Kênh: {snippet['title']}\n"
            f"🆔 ID: {data['id']}\n"
            f"📅 Ngày tạo: {snippet['publishedAt']}\n"
            f"👥 Người đăng ký: {stats.get('subscriberCount', 'Ẩn')}\n"
            f"▶️ Tổng lượt xem: {stats.get('viewCount', '0')}\n"
            f"🎥 Tổng video: {stats.get('videoCount', '0')}"
        )

        await update.message.reply_photo(snippet["thumbnails"]["high"]["url"], caption=msg)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi gọi YouTube API: {e}")

# ==== Check TikTok (demo API public, hạn chế) ====
async def check_tiktok(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <username>")
        return

    username = context.args[0].replace("@", "")

    try:
        url = f"https://www.tiktok.com/@{username}?lang=en"
        msg = f"📱 Tạm thời chỉ hỗ trợ lấy thông tin cơ bản.\n👉 Link TikTok: https://www.tiktok.com/@{username}"
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi lấy thông tin TikTok: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("yt", check_yt))
    app.add_handler(CommandHandler("tiktok", check_tiktok))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
