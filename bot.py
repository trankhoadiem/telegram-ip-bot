from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests
import os
import sys
import math
from googletrans import Translator

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== Admin Commands ====
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("🛑 Bot đang tắt...")
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("♻️ Bot đang khởi động lại...")
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("✅ Bot đang chạy bình thường!")

# ==== IP Check ====
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy thông tin cho IP: {ip}"
        info = (
            f"🌐 Thông tin IP {res['query']}:\n"
            f"🏳️ Quốc gia: {res['country']} ({res['countryCode']})\n"
            f"🏙 Thành phố: {res['regionName']} - {res['city']} ({res.get('zip','')})\n"
            f"🕒 Múi giờ: {res['timezone']}\n"
            f"📍 Tọa độ: {res['lat']}, {res['lon']}\n"
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

# ==== TikTok ==== 
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>")
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20)
        data_json = res.json()
        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text("❌ Không tải được TikTok.")
            return
        data = data_json["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title} (HQ)")
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\nĐang gửi ảnh...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== AI Mode ====
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ **Chế độ AI đang được cập nhật**. Vui lòng thử lại sau.")

async def gpt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ **Chế độ ChatGPT đang được cập nhật**. Vui lòng thử lại sau.")

async def grok_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ **Chế độ Grok (xAI) đang được cập nhật**. Vui lòng thử lại sau.")

async def gemini_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ **Chế độ Gemini (Google) đang được cập nhật**. Vui lòng thử lại sau.")

# ==== Translation ==== 
async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /translate <văn bản>")
        return
    text = " ".join(context.args)
    translator = Translator()
    translated = translator.translate(text, dest='vi')  # Mặc định dịch sang tiếng Việt
    await update.message.reply_text(f"🌐 **Dịch từ:** {text}\n➡️ **Dịch sang:** {translated.text}")

# ==== Calculator ==== 
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /calc <biểu thức>")
        return
    expression = " ".join(context.args)
    try:
        result = eval(expression)
        await update.message.reply_text(f"🔢 Kết quả: {result}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi tính toán: {e}")

# ==== Start & Help ====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini) | 📜 Dịch văn bản | 🔢 Máy tính\n\n"
        "⚡ Bot vẫn đang **cập nhật hằng ngày**, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **Hướng dẫn sử dụng BOT chi tiết** 📖\n\n"
        "✨ Bot hỗ trợ nhiều tính năng tiện ích và AI thông minh:\n\n"
        "🔹 /start - Giới thiệu bot và thông tin cơ bản.\n"
        "🔹 /help - Hiển thị danh sách lệnh kèm mô tả chi tiết.\n\n"
        "🤖 **Chế độ AI**:\n"
        "   • /ai - Bật chế độ AI và chọn model để trò chuyện.\n"
        "   • /gpt - Dùng ChatGPT để hỏi đáp, hỗ trợ thông minh.\n"
        "   • /grok - Dùng Grok (xAI), phong cách khác biệt hơn.\n"
        "   • /gemini - Dùng Gemini (Google), phản hồi nhanh và súc tích.\n"
        "   • /exit - Thoát khỏi chế độ AI.\n\n"
        "🌐 **Công cụ khác**:\n"
        "   • /ip <ip> - Kiểm tra thông tin chi tiết của một địa chỉ IP.\n"
        "   • /tiktok <link> - Tải video/ảnh TikTok không watermark.\n"
        "   • /translate <text> - Dịch văn bản sang tiếng Việt.\n"
        "   • /calc <expression> - Máy tính cơ bản (ví dụ: 2+2, 5*5).\n\n"
        "🔒 **Lệnh Admin**:\n"
        "   • /shutdown - Tắt bot.\n"
        "   • /restart - Khởi động lại bot.\n"
        "   • /startbot - Kiểm tra bot đang chạy.\n\n"
        "💡 Lưu ý: Một số lệnh yêu cầu bạn phải nhập đúng cú pháp để bot hiểu.\n"
        "👉 Hãy thử ngay bằng cách gõ /ai và chọn mô hình AI yêu thích!"
    )

# ==== MAIN ====
def main():
    app = Application.builder().token(TOKEN).build()

    # Tools
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))

    # AI
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("gpt", gpt_mode))
    app.add_handler(CommandHandler("grok", grok_mode))
    app.add_handler(CommandHandler("gemini", gemini_mode))

    # Translation & Calculator
    app.add_handler(CommandHandler("translate", translate))
    app.add_handler(CommandHandler("calc", calculate))

    # Admin commands
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))

    app.run_polling()

if __name__ == "__main__":
    main()
