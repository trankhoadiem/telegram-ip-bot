from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from datetime import datetime
import pytz

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # <-- điền token BotFather vào đây

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== /start ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ tra cứu IP, xem giờ thế giới & tải TikTok video/ảnh chất lượng cao.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Giới thiệu bot\n"
        "/help - Danh sách lệnh\n\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "👉 Ví dụ: /ip 8.8.8.8\n\n"
        "/tiktok <link> - Tải video/ảnh TikTok chất lượng cao\n"
        "👉 Ví dụ: /tiktok https://www.tiktok.com/xxxx\n\n"
        "/time - Xem giờ thế giới (ưu tiên Việt Nam hiển thị đầu tiên)\n"
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

        if data.get("hdplay") or data.get("play"):  # video
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title} (chất lượng cao nhất)")
        elif data.get("images"):  # ảnh
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")

    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== World Time ====
async def world_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    zones = [
        ("🇻🇳 Việt Nam", "Asia/Ho_Chi_Minh"),
        ("🇯🇵 Nhật Bản", "Asia/Tokyo"),
        ("🇰🇷 Hàn Quốc", "Asia/Seoul"),
        ("🇨🇳 Trung Quốc", "Asia/Shanghai"),
        ("🇦🇪 Dubai", "Asia/Dubai"),
        ("🇮🇳 Ấn Độ", "Asia/Kolkata"),
        ("🇬🇧 Anh", "Europe/London"),
        ("🇫🇷 Pháp", "Europe/Paris"),
        ("🇺🇸 Mỹ (New York)", "America/New_York"),
        ("🇺🇸 Mỹ (Los Angeles)", "America/Los_Angeles"),
        ("🇷🇺 Nga (Moscow)", "Europe/Moscow"),
        ("🇦🇺 Úc (Sydney)", "Australia/Sydney"),
    ]

    now_msg = "🕒 Giờ thế giới (hiện tại):\n\n"
    for country, zone in zones:
        tz = pytz.timezone(zone)
        time_now = datetime.now(tz)
        now_msg += f"{country} ({time_now.strftime('%Z')}): {time_now.strftime('%H:%M - %d/%m/%Y')}\n"

    await update.message.reply_text(now_msg)

# ==== Welcome New Member ====
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🎉 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!"
        )

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("time", world_time))

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()