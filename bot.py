import os
import requests
import sys
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from yt_dlp import YoutubeDL
from urllib.parse import urlparse, parse_qs

# ==== TOKEN & API KEYS ====
TOKEN = os.environ.get("TOKEN")
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY")

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== Ensure downloads folder ====
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# ==== IP Check ====
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"
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
        flag_url = f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png"
        return flag_url, info
    except Exception as e:
        return None, f"⚠️ Lỗi khi kiểm tra IP: {e}"

async def check_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=info)
    else:
        await update.message.reply_text(info)

# ==== TikTok ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>")
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20)
        data_json = res.json()
        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text("❌ Không tải được TikTok.")
            return
        data = data_json["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title} (HQ)")
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\nĐang gửi ảnh...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== YouTube ====
def get_youtube_info(youtube_url):
    query = parse_qs(urlparse(youtube_url).query)
    video_id = query.get("v")
    if not video_id:
        return None
    video_id = video_id[0]
    if not YOUTUBE_API_KEY:
        return {"title": "Unknown", "video_id": video_id}
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={YOUTUBE_API_KEY}"
    res = requests.get(url).json()
    if "items" in res and len(res["items"]) > 0:
        video = res["items"][0]["snippet"]
        return {"title": video["title"], "video_id": video_id}
    return {"title": "Unknown", "video_id": video_id}

def download_youtube(video_url, save_path="downloads/"):
    ydl_opts = {"format": "best", "outtmpl": save_path + "%(title)s.%(ext)s"}
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

async def download_youtube_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /youtube <link YouTube>")
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang tải video YouTube...")
    try:
        info = get_youtube_info(link)
        download_youtube(link)
        await waiting_msg.edit_text(f"🎬 Video {info['title']} đã tải xong. Kiểm tra thư mục `downloads/` trên server.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải video: {e}")

# ==== Start & Help ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🌐 Công cụ: Kiểm tra IP | 🎬 Tải TikTok & YouTube\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **Hướng dẫn sử dụng BOT** 📖\n\n"
        "🔹 /start - Giới thiệu bot.\n"
        "🔹 /help - Xem danh sách lệnh.\n"
        "🌐 Công cụ:\n"
        "   • /ip <ip> - Kiểm tra thông tin IP.\n"
        "   • /tiktok <link> - Tải video/ảnh TikTok.\n"
        "   • /youtube <link> - Tải video YouTube.\n"
        "🔒 Admin:\n"
        "   • /shutdown - Tắt bot.\n"
        "   • /restart - Khởi động lại bot.\n"
        "   • /startbot - Kiểm tra bot đang chạy."
    )

# ==== MAIN ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Tools
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("youtube", download_youtube_handler))

    # Admin
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()