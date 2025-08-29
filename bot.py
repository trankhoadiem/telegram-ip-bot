from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== Trạng thái người dùng cho Gemini ====
user_sessions = {}

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
        "/tiktok <link> - Tải video/ảnh TikTok chất lượng cao\n"
        "/testapi - Kiểm tra kết nối API\n"
        "/ai - Vào chế độ Chat AI (chỉ sử dụng lệnh gemini)\n"
        "/gemini - Chế độ Gemini AI (chat liên tục)\n"
        "/grok - Đang bảo trì, bot sẽ cập nhật sớm\n"
        "/gpt - Đang bảo trì, bot sẽ cập nhật sớm\n"
        "/seek - Đang bảo trì, bot sẽ cập nhật sớm\n"
        "/exit - Thoát chế độ Chat AI"
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

        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title} (chất lượng cao nhất)")

        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh gốc...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")

    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== /testapi ====
async def testapi(update, context):
    try:
        url = "https://api.example.com/healthcheck"  # Thay URL API của bạn
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            await update.message.reply_text("✅ Kết nối API thành công! API đang hoạt động bình thường.")
        else:
            await update.message.reply_text(f"⚠️ API không phản hồi đúng. Mã lỗi: {response.status_code}")
    except requests.RequestException as e:
        await update.message.reply_text(f"❌ Lỗi kết nối API: {e}")

# ==== /ai ====
async def ai_mode(update, context):
    await update.message.reply_text(
        "🎉 Bạn đã vào chế độ Chat AI.\n\n"
        "Ứng dụng có sẵn:\n"
        "/gemini - Chế độ Gemini AI (chat liên tục)\n"
        "/grok - Đang bảo trì, bot sẽ cập nhật sớm\n"
        "/gpt - Đang bảo trì, bot sẽ cập nhật sớm\n"
        "/seek - Đang bảo trì, bot sẽ cập nhật sớm\n\n"
        "Hãy sử dụng /gemini để bắt đầu!"
    )

# ==== /gemini ====
async def gemini(update, context):
    user_id = update.message.from_user.id
    user_sessions[user_id] = True
    await update.message.reply_text(
        "🌟 Bạn đã vào chế độ Gemini AI! Nhắn tin gì đi, bot sẽ trả lời bạn. "
        "Gõ /exit để thoát chế độ chat."
    )

# ==== /exit ====
async def exit_chat(update, context):
    user_id = update.message.from_user.id
    if user_sessions.get(user_id):
        user_sessions.pop(user_id, None)
        await update.message.reply_text("✅ Bạn đã thoát chế độ Gemini AI.")
    else:
        await update.message.reply_text("⚠️ Bạn không đang trong chế độ Chat AI.")

# ==== /grok, /gpt, /seek (Bảo trì) ====
async def maintenance(update, context):
    await update.message.reply_text(
        "⚠️ Lệnh này đang bảo trì, bot sẽ cập nhật sớm.\n\nHãy thử lại sau!"
    )

# ==== Xử lý tin nhắn khi đang chat Gemini ====
async def handle_message(update, context):
    user_id = update.message.from_user.id
    if user_sessions.get(user_id):
        user_input = update.message.text
        reply = f"Gemini AI trả lời: {user_input}"  # Thay bằng API thực tế nếu muốn
        await update.message.reply_text(reply)

# ==== Main ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("testapi", testapi))
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("gemini", gemini))
    app.add_handler(CommandHandler("exit", exit_chat))
    app.add_handler(CommandHandler("grok", maintenance))
    app.add_handler(CommandHandler("gpt", maintenance))
    app.add_handler(CommandHandler("seek", maintenance))

    # Tin nhắn người dùng
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
