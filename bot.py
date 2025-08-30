# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests, os, sys

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")  # Railway: đặt TOKEN = <telegram-bot-token>

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

# ==== Helper ====
async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except:
        pass  # im lặng nếu không có quyền xóa

def append_footer(text: str) -> str:
    return text + "\n\n👉 Gõ /help để xem hướng dẫn | /start"

# =======================
# 🔧 AI MODE (Bảo trì)
# =======================
MAINT_MSG = (
    "🔧 *Chức năng AI hiện đang bảo trì & nâng cấp*\n\n"
    "Các model AI như ChatGPT, Grok, Gemini tạm thời không hoạt động. "
    "Nguyên nhân có thể do cập nhật API, thay đổi cấu hình hoặc bảo mật.\n\n"
    "📌 Trong thời gian này:\n"
    "  • Các lệnh /ai, /gpt, /grok, /gemini sẽ chỉ trả về thông báo này.\n"
    "  • Bạn vẫn có thể dùng các công cụ khác như: /ip, /tiktok, /tiktokinfo.\n\n"
    "Khi bảo trì hoàn tất, các lệnh AI sẽ hoạt động lại bình thường."
)

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer(MAINT_MSG))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer("✅ Đã thoát khỏi chế độ AI."))

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer(MAINT_MSG))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer(MAINT_MSG))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer(MAINT_MSG))

# =======================
# 🔒 Admin commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        await update.message.reply_text(append_footer("⛔ Bạn không có quyền dùng lệnh này."))
        return
    await update.message.reply_text(append_footer("🛑 Bot đang tắt..."))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        await update.message.reply_text(append_footer("⛔ Bạn không có quyền dùng lệnh này."))
        return
    await update.message.reply_text(append_footer("♻️ Bot đang khởi động lại..."))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        await update.message.reply_text(append_footer("⛔ Bạn không có quyền dùng lệnh này."))
        return
    await update.message.reply_text(append_footer("✅ Bot đang chạy bình thường!"))

# =======================
# 🚀 Start / Help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer(
        "✨ *Chào mừng bạn đến với BOT* ✨\n\n"
        "🤖 Công cụ chính:  \n"
        "  • 🌐 Kiểm tra thông tin IP\n"
        "  • 🎬 Tải video/ảnh từ TikTok\n"
        "  • 📱 Lấy thông tin tài khoản TikTok\n"
        "  • 🔧 AI (hiện đang bảo trì)\n\n"
        "📌 *Phát triển*: Tô Minh Điềm – @DuRinn_LeTuanDiem"
    ))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    text = (
        "📖 *HƯỚNG DẪN CHI TIẾT CÁC LỆNH BOT*\n\n"

        "1) Lệnh cơ bản:\n"
        "   • /start — Hiển thị lời chào & thông tin bot.\n"
        "   • /help — Danh sách chi tiết các lệnh.\n\n"

        "2) Chế độ AI (đang bảo trì):\n"
        "   • /ai — Bật chế độ AI.\n"
        "   • /gpt — Chọn ChatGPT.\n"
        "   • /grok — Chọn Grok.\n"
        "   • /gemini — Chọn Gemini.\n"
        "   • /exit — Thoát chế độ AI.\n\n"

        "3) Công cụ kiểm tra IP:\n"
        "   • /ip <địa_chỉ_ip> — Kiểm tra thông tin IP: quốc gia, thành phố, ISP, tổ chức, múi giờ, tọa độ.\n"
        "     Ví dụ: `/ip 8.8.8.8`\n\n"

        "4) TikTok:\n"
        "   • /tiktok <link> — Tải nội dung từ TikTok (video/ảnh).\n"
        "   • /tiktokinfo <username> — Lấy thông tin tài khoản TikTok: tên hiển thị, UID, quốc gia, followers, likes, video, bio, avatar.\n\n"

        "5) Lệnh quản trị (chỉ admin):\n"
        "   • /shutdown — Dừng bot.\n"
        "   • /restart — Khởi động lại bot.\n"
        "   • /startbot — Kiểm tra trạng thái bot.\n\n"

        "📌 Liên hệ admin: @DuRinn_LeTuanDiem"
    )
    await update.message.reply_text(append_footer(text))

# =======================
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
        return None, f"⚠️ Lỗi IP: {e}"

async def check_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /ip <địa_chỉ_ip>"))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=append_footer(info))
    else:
        await update.message.reply_text(append_footer(info))

# =======================
# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /tiktok <link>"))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text(append_footer("❌ Không tải được TikTok."))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            await waiting_msg.delete()
            await update.message.reply_video(data.get("hdplay") or data.get("play"),
                                             caption=append_footer(f"🎬 {title}"))
        elif data.get("images"):
            for img in data["images"]:
                await update.message.reply_photo(img)
        else:
            await waiting_msg.edit_text(append_footer("⚠️ Không tìm thấy video/ảnh."))
    except Exception as e:
        await waiting_msg.edit_text(append_footer(f"⚠️ Lỗi TikTok: {e}"))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text(append_footer("👉 Dùng: /tiktokinfo <username>"))
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy info @{username}...")
    try:
        api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
        res = requests.get(api_url, headers=HEADERS, timeout=15).json()
        user = res.get("data", {})
        caption = (
            f"📱 TikTok @{user.get('unique_id', username)}\n"
            f"👤 {user.get('nickname','N/A')}\n"
            f"🌍 Quốc gia: {user.get('region','?')}\n"
            f"👥 Followers: {user.get('follower_count','?')}\n"
            f"❤️ Likes: {user.get('total_favorited','?')}\n"
            f"🎬 Video: {user.get('aweme_count','?')}\n"
            f"📝 Bio: {user.get('signature','')}"
        )
        avatar = user.get("avatar")
        if avatar:
            await waiting_msg.delete()
            await update.message.reply_photo(avatar, caption=append_footer(caption))
        else:
            await waiting_msg.edit_text(append_footer(caption))
    except Exception as e:
        await waiting_msg.edit_text(append_footer(f"⚠️ Lỗi TikTok info: {e}"))

# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(TOKEN).build()

    # AI
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("exit", exit_ai))
    app.add_handler(CommandHandler("gpt", gpt))
    app.add_handler(CommandHandler("grok", grok))
    app.add_handler(CommandHandler("gemini", gemini))

    # Tools
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("tiktokinfo", tiktok_info))

    # Admin
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
