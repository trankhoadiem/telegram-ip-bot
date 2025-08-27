import logging
import re
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import io

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token from environment variable or replace with your token
TOKEN = os.environ.get("TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")

# TikWM API for TikTok downloading
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== /start ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ tra cứu IP & tải YouTube/TikTok video/ảnh chất lượng cao.\n\n"
        "📌 Các thành viên phát triển BOT:\n"
        " 👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        " 👤 Telegram Support – @Telegram\n"
        " 🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/tiktok <link> - Tải video/ảnh TikTok\n"
        "/yt <link> - Tải video YouTube Shorts\n"
        "/sc <link> - Tải âm thanh SoundCloud\n"
        "/meme <link> <chữ> - Tạo meme từ ảnh\n"
        "/tts <text> - Chuyển văn bản thành giọng nói\n"
        "/weather <city> - Thông tin thời tiết"
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

# ==== TikTok Downloader ====
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
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20)
        data_json = res.json()

        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text("❌ Không tải được TikTok. Vui lòng kiểm tra lại link!")
            return

        data = data_json["data"]
        title = data.get("title", "TikTok")

        # Nếu là video
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title} (chất lượng cao nhất)")

        # Nếu là bài ảnh
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh gốc...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)

        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")

    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== YouTube Downloader (Shorts) ====
async def download_youtube(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /yt <link YouTube>")
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link YouTube, vui lòng chờ...")

    try:
        ydl_opts = {
            'format': 'bestaudio/best',  # Chọn chất lượng tốt nhất
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        with YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            video_url = info_dict.get('url', None)

            await waiting_msg.delete()
            await update.message.reply_video(video_url, caption=f"🎬 YouTube Short: {info_dict.get('title', 'Video')}")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải video YouTube: {e}")

# ==== SoundCloud Downloader ====
async def download_soundcloud(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /sc <link SoundCloud>")
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link SoundCloud, vui lòng chờ...")

    try:
        scdl_url = f"https://scdl.com/{link}"
        await waiting_msg.delete()
        await update.message.reply_text(f"Tải nhạc từ SoundCloud tại: {scdl_url}")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải từ SoundCloud: {e}")

# ==== Text to Speech (TTS) ====
async def text_to_speech(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tts <văn bản>")
        return

    text = ' '.join(context.args)

    try:
        tts = gTTS(text, lang='vi')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            await update.message.reply_audio(open(tmp.name, 'rb'), caption="Giọng nói của tôi")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi tạo giọng nói: {e}")

# ==== Meme Creator ====
async def create_meme(update, context):
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("👉 Dùng: /meme <link image> <chữ>")
        return

    image_url = context.args[0]
    text = ' '.join(context.args[1:])

    try:
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))

        # Thêm chữ vào ảnh
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((10, 10), text, font=font, fill="white")

        # Lưu ảnh và gửi lại
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        await update.message.reply_photo(img_byte_arr)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi tạo meme: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("yt", download_youtube))
    app.add_handler(CommandHandler("sc", download_soundcloud))
    app.add_handler(CommandHandler("tts", text_to_speech))
    app.add_handler(CommandHandler("meme", create_meme))

    # Run the bot
    app.run_polling()

if __name__ == "__main__":
    main()
