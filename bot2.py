from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import yt_dlp
import os

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT 2** ✨\n\n"
        "🤖 Công cụ tra cứu IP & tải TikTok video/ảnh chất lượng cao.\n\n"
        "📌 Các thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @TraMy_2011\n"
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
        "/tiktok <link> - Tải video/ảnh TikTok chất lượng cao\n"
        "/biaYT <link video YouTube> - Tải ảnh bìa YouTube"
    )

# ==== Check IP ====
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()

        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"

        info = (
            f"🌍 Thông tin IP {res['query']}:\n"
            f"🗺 Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Khu vực: {res['regionName']} - {res['city']} ({res.get('zip','')})\n"
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
    try:
        await update.message.delete()
    except:
        pass

    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return

    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=info)
    else:
        await update.message.reply_text(info)

# ==== TikTok Downloader with yt-dlp ====
async def download_tiktok(update, context):
    try:
        await update.message.delete()
    except:
        pass

    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>")
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok, vui lòng chờ...")

    try:
        # Sử dụng yt-dlp để tải video TikTok với chất lượng cao nhất
        ydl_opts = {
            'format': 'bestaudio/best',  # Tải chất lượng video cao nhất
            'outtmpl': 'downloads/%(id)s.%(ext)s',  # Tùy chọn tải xuống
            'quiet': True,  # Tắt log
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            video_url = info_dict.get("url")
            title = info_dict.get("title", "TikTok video")

            await waiting_msg.delete()
            await update.message.reply_video(video_url, caption=f"🎬 {title} (chất lượng cao nhất)")

    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== YouTube Thumbnail Downloader ====
async def download_youtube_thumbnail(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /biaYT <link video YouTube>")
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang tải ảnh bìa video YouTube, vui lòng chờ...")

    try:
        video_id = link.split("v=")[-1]
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
        
        res = requests.get(thumbnail_url)

        if res.status_code == 200:
            await waiting_msg.delete()
            await update.message.reply_photo(thumbnail_url, caption="🎬 Ảnh bìa video YouTube")
        else:
            await waiting_msg.edit_text("⚠️ Không thể lấy ảnh bìa từ YouTube.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải ảnh bìa YouTube: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("biaYT", download_youtube_thumbnail))  # Lệnh tải ảnh bìa YouTube

    print("🤖 Bot 2 đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
