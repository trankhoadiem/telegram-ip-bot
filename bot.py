import logging
import re
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from yt_dlp import YoutubeDL

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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/tiktok <link> - Tải video/ảnh TikTok chất lượng cao\n"
        "🌐 Gửi link YouTube hoặc TikTok để tải video trực tiếp"
    )

async def check_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.delete()
    except:
        pass
    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0].strip()
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            await update.message.reply_text(f"❌ Không tìm thấy thông tin cho IP: {ip}")
            return
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
        await update.message.reply_photo(flag_url, caption=info)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi kiểm tra IP: {e}")

async def download_youtube(url: str, chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': f'video_{chat_id}.%(ext)s',
            'merge_output_format': 'mp4',
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        logger.error(f"Error downloading YouTube video: {e}")
        return None

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        # If it's a video
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title} (chất lượng cao nhất)")
        # If it's an image post
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh gốc...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    chat_id = update.message.chat_id

    # Check for YouTube URL
    youtube_regex = r'(https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[^\s]+)'
    youtube_url = re.search(youtube_regex, message)

    if youtube_url:
        await update.message.reply_text("⏳ Đang tải video YouTube...")
        filename = await download_youtube(youtube_url.group(0), chat_id, context)
        if filename and os.path.exists(filename):
            with open(filename, 'rb') as video:
                await update.message.reply_video(video=video)
            os.remove(filename)
        else:
            await update.message.reply_text("❌ Không tải được video YouTube.")
    else:
        await update.message.reply_text("🌐 Vui lòng gửi link YouTube hoặc dùng /tiktok <link> cho TikTok.")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🎉 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    # Message handler for YouTube links
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
