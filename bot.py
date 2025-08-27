from telegram.ext import Application, CommandHandler
import requests
import os

TOKEN = os.environ.get("TOKEN")   # Token bot Telegram (set trên Railway)

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Đây là công cụ hỗ trợ tra cứu thông tin IP và tải video TikTok nhanh chóng.\n\n"
        "📌 Các thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem danh sách lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/tiktok <link> - Tải video TikTok (không logo)"
    )

# ==== Check IP ====
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url).json()

        if res["status"] == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"

        info = (
            f"🌍 Thông tin IP {res['query']}:\n"
            f"🗺 Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Khu vực: {res['regionName']} - {res['city']} ({res['zip']})\n"
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
    ip = context.args[0]
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=info)
    else:
        await update.message.reply_text(info)

# ==== Download TikTok Video ====
async def download_tiktok(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link video TikTok>")
        return

    link = context.args[0]
    try:
        api = "https://www.tikwm.com/api/"
        res = requests.post(api, data={"url": link}).json()

        if res.get("code") != 0:
            await update.message.reply_text("❌ Không tải được video TikTok. Kiểm tra lại link!")
            return

        video_url = res["data"]["play"]   # Link video không logo
        title = res["data"].get("title", "TikTok video")

        await update.message.reply_video(video_url, caption=f"🎬 {title}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi tải video TikTok: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
