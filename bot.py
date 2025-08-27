from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import yt_dlp
import os
import soundcloud

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== SoundCloud API ====
SC_CLIENT_ID = 'YOUR_SOUNDCLOUD_CLIENT_ID'  # Đăng ký API key từ SoundCloud

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
        "/sc <link> - Tải âm thanh SoundCloud"
    )

# ==== SoundCloud Downloader ====
async def download_soundcloud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /sc <link SoundCloud>")
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link SoundCloud, vui lòng chờ...")
    
    try:
        # Khởi tạo client SoundCloud
        client = soundcloud.Client(client_id=SC_CLIENT_ID)
        
        # Lấy track từ link SoundCloud
        track = client.get('/resolve', url=link)
        
        if track:
            await waiting_msg.edit_text(f"🎵 Đang tải nhạc: {track.title}")
            stream_url = track.stream_url
            audio_url = f"{stream_url}?client_id={SC_CLIENT_ID}"
            await update.message.reply_audio(audio_url, caption=f"🎶 {track.title}")
        else:
            await waiting_msg.edit_text("❌ Không tải được từ SoundCloud, vui lòng kiểm tra lại link.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải từ SoundCloud: {e}")

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

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("sc", download_soundcloud))

    # Run the bot
    app.run_polling()

if __name__ == "__main__":
    main()
