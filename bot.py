from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
import os

TOKEN = os.environ.get("TOKEN")   # token bot Telegram (Railway set)
FB_TOKEN = os.environ.get("FB_TOKEN")  # token Facebook Graph API

# Lệnh /start
async def start(update, context):
    await update.message.reply_text(
        "👋 Xin chào! Tôi là Bot Check IP & Facebook.\n"
        "Gõ /help để xem cách dùng."
    )

# Lệnh /help
async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/fb <id hoặc username> - Lấy thông tin Facebook"
    )

# Hàm xử lý check IP
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url).json()

        if res["status"] == "fail":
            return f"❌ Không tìm thấy thông tin cho IP: {ip}"

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
        return info
    except Exception as e:
        return f"⚠️ Lỗi khi kiểm tra IP: {e}"

# Lệnh /ip
async def check_ip(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0]
    info = get_ip_info(ip)
    await update.message.reply_text(info)

# Lệnh /fb
async def check_fb(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /fb 4 hoặc /fb zuck")
        return

    fb_id = context.args[0]
    url = f"https://graph.facebook.com/{fb_id}"
    params = {
        "fields": "id,name,birthday,location,followers_count",
        "access_token": FB_TOKEN
    }

    try:
        r = requests.get(url, params=params).json()
        if "error" in r:
            await update.message.reply_text(f"❌ Lỗi: {r['error']['message']}")
            return

        msg = f"👤 Tên: {r.get('name')}\n🆔 ID: {r.get('id')}\n"
        if "birthday" in r:
            msg += f"🎂 Ngày sinh: {r['birthday']}\n"
        if "location" in r:
            msg += f"📍 Nơi sống: {r['location']['name']}\n"
        if "followers_count" in r:
            msg += f"👥 Người theo dõi: {r['followers_count']}\n"

        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi gọi Facebook API: {e}")

# Main
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("fb", check_fb))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
