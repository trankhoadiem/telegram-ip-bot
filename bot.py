from telegram.ext import Application, CommandHandler
import requests
import os
import yt_dlp

TOKEN = os.environ.get("TOKEN")   # Token bot Telegram (set trên Railway)

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Đây là công cụ hỗ trợ tra cứu IP, tải video TikTok & YouTube nhanh chóng.\n\n"
        "📌 Bot được phát triển bởi:\n"
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
        "/tiktok <link> - Tải video TikTok\n"
        "/yt <link> - Tải video YouTube"
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

# ==== Tải video TikTok ====
async def download_tiktok(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link>")
        return
    url = context.args[0]

    try:
        ydl_opts = {"outtmpl": "video.mp4"}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open("video.mp4", "rb") as f:
            await update.message.reply_video(f, caption="✅ Video TikTok của bạn đây!")
        os.remove("video.mp4")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi tải TikTok: {e}")

# ==== Tải video YouTube ====
async def download_youtube(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /yt <link>")
        return
    url = context.args[0]

    try:
        ydl_opts = {
            "format": "mp4",
            "outtmpl": "yt_video.mp4"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        with open("yt_video.mp4", "rb") as f:
            await update.message.reply_video(f, caption="✅ Video YouTube của bạn đây!")
        os.remove("yt_video.mp4")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi tải YouTube: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("yt", download_youtube))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
