from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import datetime
import pytz

# ==== TOKEN ====
TOKEN = "8409398524:AAG7pxkslC_fLUWvvcGLgmZwWQ-oXZqP5Hg"

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
        "📌 Các thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update, context):
    text = """
📖 **Hướng dẫn sử dụng BOT:**

/start - Giới thiệu bot & tác giả
/help - Hiển thị hướng dẫn chi tiết

/time <quốc gia> - Xem thời gian hiện tại
👉 Ví dụ: /time vietnam, /time dubai, /time usa

/id - Xem ID của bạn và ID nhóm/chat
👉 Ví dụ: /id

/info - Xem thông tin tài khoản Telegram của bạn
👉 Ví dụ: /info

/ip <địa chỉ ip> - Kiểm tra thông tin IP (quốc gia, thành phố, ISP...)
👉 Ví dụ: /ip 8.8.8.8

/tiktok <link TikTok> - Tải video/ảnh TikTok chất lượng cao, không logo
👉 Ví dụ: /tiktok https://www.tiktok.com/@username/video/123456789

📌 Ngoài ra bot sẽ tự động **chào mừng thành viên mới** khi họ tham gia nhóm.
"""
    await update.message.reply_text(text, disable_web_page_preview=True)

# ==== /time ====
TIMEZONES = {
    "vietnam": "Asia/Ho_Chi_Minh",
    "vn": "Asia/Ho_Chi_Minh",
    "dubai": "Asia/Dubai",
    "uae": "Asia/Dubai",
    "usa": "America/New_York",
    "my": "America/New_York",
    "newyork": "America/New_York",
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
            await update.message.reply_text(f"⏰ Thời gian hiện tại ở {country.title()}: {now}")
        else:
            await update.message.reply_text("❌ Quốc gia không được hỗ trợ. Gõ /help để xem gợi ý.")
    else:
        vn_tz = pytz.timezone("Asia/Ho_Chi_Minh")
        now = datetime.datetime.now(vn_tz).strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(f"⏰ Thời gian hiện tại (Việt Nam): {now}")

# ==== /id ====
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    await update.message.reply_text(f"🆔 User ID: {user_id}\n💬 Chat ID: {chat_id}")

# ==== /info ====
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = f"""
👤 **Thông tin người dùng:**
- Họ tên: {user.first_name} {user.last_name or ""}
- Username: @{user.username}
- ID: {user.id}
    """
    await update.message.reply_text(text)

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
            await update.message.reply_video(url, caption=f"🎬 {title} (chất lượng cao)")

        # Nếu là bài ảnh
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)

        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")

    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== Welcome New Member ====
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🎉 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!"
        )

# ==== MAIN ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("time", time))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("info", info))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
