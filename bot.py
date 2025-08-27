from telegram.ext import Application, CommandHandler, MessageHandler, filters
import requests
import os

TOKEN = os.environ.get("TOKEN")  # Railway sẽ set TOKEN

async def start(update, context):
    await update.message.reply_text(
        "👋 Xin chào! Tôi là Bot Check IP.\n"
        "Gõ /help để xem cách dùng."
    )

async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "👉 Gõ một địa chỉ IP bất kỳ để tra cứu\n"
        "Ví dụ: 8.8.8.8"
    )

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

async def check_ip(update, context):
    ip = update.message.text.strip()
    info = get_ip_info(ip)
    await update.message.reply_text(info)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_ip))

    print("🤖 Bot Check IP đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
