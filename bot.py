from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests

# 🌐 IP checker
# =======================
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Không tìm thấy IP: {ip}"
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
        return f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png", info
    except Exception as e:
        return None, f"❌ Lỗi khi lấy thông tin IP: {e}"

# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("/tiktok <link> để tải video/ảnh TikTok")
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok...")
    try:
        res = requests.post("https://www.tikwm.com/api/", data={"url": link}, headers={"User-Agent": "Mozilla/5.0"}, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Không tải được TikTok")
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            msg = await update.message.reply_video(
                data.get("hdplay") or data.get("play"),
                caption=f"🎬 {title}"
            )
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
        else:
            await update.message.reply_text("❌ Không tìm thấy video hoặc ảnh.")
    except Exception as e:
        await waiting_msg.edit_text(f"❌ Lỗi: {str(e)}")

# 🔒 Admin commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot đang tắt... 🛑")
    await context.bot.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot đang khởi động lại... 🔄")
    await context.bot.stop()

async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot đang chạy bình thường ✅")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.reply_to_message.from_user.id
    await update.message.reply_text(f"🔒 Đã khóa mõm người dùng {user_id} trong 1 phút.")
    # Logic mute user

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.reply_to_message.from_user.id
    await update.message.reply_text(f"🔓 Mở khóa người dùng {user_id}.")
    # Logic unmute user

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.reply_to_message.from_user.id
    await update.message.reply_text(f"👋 Đã đuổi người dùng {user_id} ra khỏi nhóm.")
    # Logic kick user

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.reply_to_message.from_user.id
    await update.message.reply_text(f"🚫 Đã cấm người dùng {user_id} khỏi nhóm.")
    # Logic ban user

# Lệnh AI chung cho tất cả các model
async def ai_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Dùng /ask để hỏi GPT-5 của Tô Minh Điềm")

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Dùng /ask để hỏi GPT-5 của Tô Minh Điềm")

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Dùng /ask để hỏi GPT-5 của Tô Minh Điềm")

# /start và /help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Chào mừng bạn đến với BOT ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT-5)\n\n"
        "⚡ Bot vẫn đang cập nhật hằng ngày, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @TraMy_2011\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng."
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Hướng dẫn sử dụng BOT chi tiết 📖\n\n"
        "✨ Bot hỗ trợ nhiều tính năng tiện ích và AI thông minh:\n\n"
        "🔹 /start – Giới thiệu bot và thông tin cơ bản.\n"
        "🔹 /help – Hiển thị danh sách lệnh kèm mô tả chi tiết.\n\n"
        "🤖 Chế độ AI:\n"
        "• /ai – Bật chế độ AI và chọn model để trò chuyện.\n"
        "• /gpt – Dùng ChatGPT Plus – GPT-5, hỗ trợ hỏi đáp thông minh.\n"
        "• /grok – Dùng Grok (xAI), phong cách khác biệt hơn.\n"
        "• /gemini – Dùng Gemini (Google), phản hồi nhanh và súc tích.\n"
        "• /exit – Thoát khỏi chế độ AI.\n"
        "• /ask <câu hỏi> – Lệnh gọi nhanh ChatGPT Plus – GPT-5.\n"
        "👉 Ví dụ: /ask Viết cho tôi một đoạn giới thiệu về công nghệ AI\n\n"
        "🌐 Công cụ khác:\n"
        "• /ip <ip> – Kiểm tra thông tin chi tiết của một địa chỉ IP.\n"
        "• /tiktok <link> – Tải video/ảnh TikTok không watermark.\n"
        "• /testapi – Kiểm tra trạng thái các API key (GPT, Grok, Gemini).\n\n"
        "🔒 Lệnh Admin:\n"
        "• /shutdown – Tắt bot.\n"
        "• /restart – Khởi động lại bot.\n"
        "• /startbot – Kiểm tra bot đang chạy.\n"
        "• /mute – 🔒 Khóa chat.\n"
        "• /unmute – 🔓 Mở chat.\n"
        "• /kick – Đuổi thành viên ra khỏi nhóm.\n"
        "• /ban – Cấm thành viên.\n\n"
    )

# Cấu hình các handler
application = Application.builder().token("YOUR_BOT_TOKEN").build()

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help))
application.add_handler(CommandHandler("ai", ai_reply))
application.add_handler(CommandHandler("grok", grok))
application.add_handler(CommandHandler("gemini", gemini))
application.add_handler(CommandHandler("ip", ip))
application.add_handler(CommandHandler("tiktok", download_tiktok))

# Start bot
application.run_polling()
