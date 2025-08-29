from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import datetime
import pytz
import os

# ==== TOKEN (lấy từ Railway ENV) ====
TOKEN = os.getenv("TOKEN")  # Bạn set ở Railway Variables

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT Tiện Ích** ✨\n\n"
        "🤖 Công cụ tra cứu IP, tải TikTok video/ảnh chất lượng cao và nhiều tiện ích khác.\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update, context):
    text = """
📖 **Hướng dẫn sử dụng BOT:**

/start - Giới thiệu bot
/help - Hiển thị hướng dẫn chi tiết

/time <quốc gia> - Xem giờ thế giới
👉 Ví dụ: /time vietnam, /time dubai, /time usa

/id - Xem ID của bạn
/info - Xem thông tin tài khoản
/ip <ip> - Kiểm tra thông tin IP
/tiktok <link> - Tải video/ảnh TikTok không logo
"""
    await update.message.reply_text(text, disable_web_page_preview=True)

# ==== /time ====
TIMEZONES = {
    "vietnam": "Asia/Ho_Chi_Minh",
    "vn": "Asia/Ho_Chi_Minh",
    "dubai": "Asia/Dubai",
    "usa": "America/New_York",
    "newyork": "America/New_York",
    "losangeles": "America/Los_Angeles",
    "london": "Europe/London",
    "uk": "Europe/London",
    "tokyo": "Asia/Tokyo",
    "japan": "Asia/Tokyo"
}

async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        country = context.args[0].lower()
        if country in TIMEZONES:
            tz = pytz.timezone(TIMEZONES[country])
            now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            await update.message.reply_text(f"⏰ {country.title()}: {now}")
        else:
            await update.message.reply_text("❌ Quốc gia không được hỗ trợ. Gõ /help để xem.")
    else:
        tz = pytz.timezone("Asia/Ho_Chi_Minh")
        now = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(f"⏰ Việt Nam: {now}")

# ==== /id ====
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆔 User ID: {update.message.from_user.id}\n💬 Chat ID: {update.message.chat_id}"
    )

# ==== /info ====
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    await update.message.reply_text(
        f"👤 Họ tên: {user.first_name} {user.last_name or ''}\n"
        f"🔗 Username: @{user.username}\n"
        f"🆔 ID: {user.id}"
    )

# ==== IP Lookup ====
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"

        info = (
            f"🌍 IP {res['query']}:\n"
            f"🗺 Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Thành phố: {res['city']} ({res['regionName']})\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📡 ISP: {res['isp']}\n"
            f"🏢 Tổ chức: {res['org']}"
        )
        return None, info
    except Exception as e:
        return None, f"⚠️ Lỗi: {e}"

async def check_ip(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    _, info = get_ip_info(context.args[0].strip())
    await update.message.reply_text(info)

# ==== TikTok Downloader ====
async def download_tiktok(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>")
        return

    waiting_msg = await update.message.reply_text("⏳ Đang tải TikTok...")

    try:
        res = requests.post(TIKWM_API, data={"url": context.args[0]}, headers=HEADERS, timeout=20)
        data = res.json()
        if data.get("code") != 0 or "data" not in data:
            await waiting_msg.edit_text("❌ Không tải được video!")
            return

        d = data["data"]
        if d.get("hdplay") or d.get("play"):
            await waiting_msg.delete()
            await update.message.reply_video(d.get("hdplay") or d.get("play"))
        elif d.get("images"):
            for img in d["images"]:
                await update.message.reply_photo(img)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi: {e}")

# ==== Welcome ====
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"🎉 Chào mừng {member.full_name}!")

# ==== MAIN ====
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("time", time))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
