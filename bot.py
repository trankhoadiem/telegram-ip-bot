import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==== TOKEN ====
TOKEN = 'YOUR_BOT_TOKEN'  # Thay 'YOUR_BOT_TOKEN' bằng token thật của bạn

# ==== Snaptik Downloader ====
def download_tiktok(url):
    try:
        download_url = f"https://snaptik.vn/api/download?url={url}"
        res = requests.get(download_url)
        if res.status_code == 200:
            return res.text  # Hoặc URL tải về
        else:
            return "❌ Không tải được video TikTok."
    except Exception as e:
        return f"⚠️ Lỗi khi tải video TikTok: {e}"

# ==== YouTube Downloader ====
def download_youtube(url):
    try:
        download_url = f"https://y2-mate.download/yt?url={url}"
        res = requests.get(download_url)
        if res.status_code == 200:
            return res.text  # Hoặc URL tải về
        else:
            return "❌ Không tải được video YouTube."
    except Exception as e:
        return f"⚠️ Lỗi khi tải video YouTube: {e}"

# ==== SoundCloud Downloader ====
def download_soundcloud(url):
    try:
        download_url = f"https://taivideoaz.com/tai-nhac-soundcloud/?url={url}"
        res = requests.get(download_url)
        if res.status_code == 200:
            return res.text  # Hoặc URL tải về
        else:
            return "❌ Không tải được nhạc từ SoundCloud."
    except Exception as e:
        return f"⚠️ Lỗi khi tải nhạc: {e}"

# ==== Start Command ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ tải video YouTube, TikTok và nhạc SoundCloud!\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== Help Command ====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/sc <link> - Tải nhạc từ SoundCloud\n"
        "/yt <link> - Tải video từ YouTube\n"
        "/tiktok <link> - Tải video từ TikTok"
    )

# ==== Download SoundCloud ====
async def download_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /sc <link SoundCloud>")
        return
    link = context.args[0].strip()
    result = download_soundcloud(link)
    await update.message.reply_text(result)

# ==== Download YouTube ====
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /yt <link YouTube>")
        return
    link = context.args[0].strip()
    result = download_youtube(link)
    await update.message.reply_text(result)

# ==== Download TikTok ====
async def download_tiktok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>")
        return
    link = context.args[0].strip()
    result = download_tiktok(link)
    await update.message.reply_text(result)

# ==== Main ==== 
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("sc", download_music))  # SoundCloud
    app.add_handler(CommandHandler("yt", download_video))  # YouTube
    app.add_handler(CommandHandler("tiktok", download_tiktok_handler))  # TikTok

    app.run_polling()

if __name__ == "__main__":
    main()
