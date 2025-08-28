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

# ==== /start ====
async def start(update, context):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok\n\n"
        "⚡ Bot vẫn đang **cập nhật hằng ngày**, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng."
    )

# ==== /help ====
async def help_command(update, context):
    await update.message.reply_text(
        "📖 **Hướng dẫn sử dụng BOT chi tiết** 📖\n\n"
        "🔹 /start - Giới thiệu bot và thông tin cơ bản.\n"
        "🔹 /help - Hiển thị danh sách lệnh kèm mô tả chi tiết.\n"
        "🔹 /ip <ip> - Kiểm tra thông tin chi tiết của một địa chỉ IP.\n"
        "🔹 /tiktok <link> - Tải video/ảnh TikTok không watermark.\n\n"
        "🔒 **Lệnh Admin**:\n"
        "   • /shutdown - Tắt bot.\n"
        "   • /restart - Khởi động lại bot.\n"
        "   • /startbot - Kiểm tra bot đang chạy.\n"
    )

# ==== Kiểm tra IP ====
async def check_ip(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip <địa chỉ IP>")
        return
    
    ip = context.args[0]
    url = f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,query,isp,org"
    try:
        res = requests.get(url, timeout=10).json()
        if res.get("status") != "success":
            await update.message.reply_text(f"❌ Lỗi: {res.get('message', 'Không xác định')}")
            return

        msg = (
            f"🌍 **Thông tin IP {res['query']}**\n"
            f"   • Quốc gia: {res['country']}\n"
            f"   • Khu vực: {res['regionName']}\n"
            f"   • Thành phố: {res['city']}\n"
            f"   • ISP: {res['isp']}\n"
            f"   • Tổ chức: {res['org']}"
        )
        await update.message.reply_text(msg)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi kiểm tra IP: {e}")

# ==== Tải video TikTok ====
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

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
