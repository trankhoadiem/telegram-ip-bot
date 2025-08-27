from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import os
from uuid import uuid4

TOKEN = os.environ.get("TOKEN")

# Cache tạm thời cho các URL (tránh callback_data quá dài)
CACHE = {}

TIKWM_API = "https://www.tikwm.com/api/"
TIKWM_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ tra cứu IP & tải TikTok video/ảnh chất lượng cao.\n\n"
        "📌 Các thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update, context):
    await update.message.reply_text(
        "📖 Lệnh có sẵn:\n\n"
        "/start - Bắt đầu\n"
        "/help - Trợ giúp\n"
        "/ip <địa chỉ ip> - Kiểm tra thông tin IP\n"
        "/tiktok <link> - Tải video/ảnh TikTok"
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

async def check_ip(update, context):
    # Xoá tin nhắn user (nếu không được thì bỏ qua)
    try:
        await update.message.delete()
    except:
        pass

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
    # Xoá tin nhắn user
    try:
        await update.message.delete()
    except:
        pass

    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link video TikTok>")
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok, vui lòng chờ...")

    try:
        # Gọi API
        res = requests.post(TIKWM_API, data={"url": link}, headers=TIKWM_HEADERS, timeout=20)
        data_json = res.json()

        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text("❌ Không tải được TikTok. Vui lòng kiểm tra lại link!")
            return

        data = data_json["data"]
        title = data.get("title", "TikTok")

        # Là VIDEO
        if data.get("play"):
            buttons = []

            # Helper tạo nút + cache token
            def add_button(label, ftype, url):
                token = uuid4().hex[:16]
                CACHE[token] = {"type": ftype, "url": url}
                buttons.append([InlineKeyboardButton(label, callback_data=token)])

            # 480p (play) luôn có
            add_button("📹 480p", "video", data["play"])

            # 1080p (hdplay) nếu có
            if data.get("hdplay"):
                add_button("📹 1080p", "video", data["hdplay"])

            # Audio nếu có
            if data.get("music"):
                add_button("🎵 Audio (MP3)", "audio", data["music"])

            reply_markup = InlineKeyboardMarkup(buttons)
            await waiting_msg.edit_text(f"🎬 {title}\n\nChọn chất lượng tải:", reply_markup=reply_markup)

        # Là BÀI ẢNH
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh gốc...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)

        else:
            await waiting_msg.edit_text("⚠️ Không nhận diện được video/ảnh từ link này.")

    except Exception as e:
        # Trường hợp JSON lỗi hoặc bị chặn Cloudflare
        try:
            await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")
        except:
            pass

# ==== Xử lý khi bấm nút chọn chất lượng ====
async def button(update, context):
    query = update.callback_query
    await query.answer()

    token = query.data
    payload = CACHE.get(token)

    if not payload:
        await query.message.reply_text("⏰ Nút đã hết hạn, vui lòng dùng lại /tiktok với link đó.")
        return

    filetype = payload["type"]
    url = payload["url"]

    try:
        if filetype == "audio":
            await query.message.reply_audio(url, caption="🎵 Nhạc gốc TikTok")
        elif filetype == "video":
            await query.message.reply_video(url, caption="🎬 Video TikTok")
    except Exception as e:
        await query.message.reply_text(f"⚠️ Lỗi khi gửi file: {e}")

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
