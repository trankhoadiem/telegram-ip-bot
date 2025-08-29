from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import datetime
import pytz
import os

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")  # Hoặc thay trực tiếp TOKEN = "123456:ABC..."

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== /start ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT Tiện Ích** ✨\n\n"
        "🤖 Công cụ tra cứu IP, tải TikTok video/ảnh chất lượng cao và nhiều tiện ích khác.\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
📖 **Hướng dẫn sử dụng BOT:**

/start - Giới thiệu bot & tác giả
/help - Hiển thị hướng dẫn chi tiết

/time - Xem giờ thế giới (Việt Nam, Dubai, Mỹ, Nhật, Anh)
/time <quốc gia> - Xem giờ riêng 1 nước
👉 Ví dụ:
/time vietnam
/time dubai
/time usa
/time japan
/time london

/id - Xem ID của bạn và ID nhóm/chat
/info - Xem thông tin tài khoản của bạn
/ip <ip> - Kiểm tra thông tin IP
/tiktok <link> - Tải TikTok video/ảnh không logo

📌 Ngoài ra bot sẽ tự động **chào mừng thành viên mới** khi họ tham gia nhóm.
"""
    await update.message.reply_text(text, disable_web_page_preview=True)

# ==== /time ====
async def time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Danh sách thành phố + alias để người dùng gõ dễ hơn
        cities = {
            "vietnam": ("🇻🇳 Việt Nam", "Asia/Ho_Chi_Minh"),
            "vn": ("🇻🇳 Việt Nam", "Asia/Ho_Chi_Minh"),
            "dubai": ("🇦🇪 Dubai", "Asia/Dubai"),
            "usa": ("🇺🇸 Mỹ (New York)", "America/New_York"),
            "us": ("🇺🇸 Mỹ (New York)", "America/New_York"),
            "newyork": ("🇺🇸 Mỹ (New York)", "America/New_York"),
            "la": ("🇺🇸 Mỹ (Los Angeles)", "America/Los_Angeles"),
            "losangeles": ("🇺🇸 Mỹ (Los Angeles)", "America/Los_Angeles"),
            "japan": ("🇯🇵 Nhật Bản", "Asia/Tokyo"),
            "tokyo": ("🇯🇵 Nhật Bản", "Asia/Tokyo"),
            "london": ("🇬🇧 London", "Europe/London"),
            "uk": ("🇬🇧 London", "Europe/London"),
            "anh": ("🇬🇧 London", "Europe/London"),
        }

        # Nếu có đối số => lấy giờ riêng nước đó
        if context.args:
            key = context.args[0].lower()
            if key in cities:
                city, tz = cities[key]
                now = datetime.datetime.now(pytz.timezone(tz))
                await update.message.reply_text(
                    f"⏰ Giờ tại {city}: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                )
                return
            else:
                await update.message.reply_text("❌ Quốc gia này chưa hỗ trợ. Gõ /help để xem danh sách.")
                return

        # Nếu không có đối số => in tất cả
        result = "⏰ **Giờ thế giới hiện tại:**\n\n"
        world_timezones = {
            "🇻🇳 Việt Nam": "Asia/Ho_Chi_Minh",
            "🇦🇪 Dubai": "Asia/Dubai",
            "🇺🇸 Mỹ (New York)": "America/New_York",
            "🇺🇸 Mỹ (Los Angeles)": "America/Los_Angeles",
            "🇯🇵 Nhật Bản": "Asia/Tokyo",
            "🇬🇧 London": "Europe/London"
        }
        for city, tz in world_timezones.items():
            now = datetime.datetime.now(pytz.timezone(tz))
            result += f"{city}: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"

        await update.message.reply_text(result)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi lấy giờ: {e}")

# ==== /id ====
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id = update.message.chat.id
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

# ==== TikTok Downloader ====
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
