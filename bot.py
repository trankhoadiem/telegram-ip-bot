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
        # im lặng nếu không có quyền xóa
        pass

def append_footer(text: str) -> str:
    return text + "\n\n👉 Gõ /help để xem hướng dẫn | /start"

# =======================
# 🔧 AI MODE (Bảo trì - thông báo chi tiết)
# =======================
MAINT_MSG = (
    "🔧 *Chức năng AI đang trong giai đoạn bảo trì & nâng cấp*\n\n"
    "Hiện tại các model AI (ChatGPT, Grok, Gemini) tạm thời **không hoạt động** trên bot này vì đang được "
    "bảo trì, cập nhật cấu hình và xử lý giới hạn truy cập. Những thay đổi có thể bao gồm cập nhật API key, "
    "cấu hình bảo mật hoặc chỉnh sửa logic để cải thiện chất lượng câu trả lời.\n\n"
    "• *Điều đó có nghĩa gì?*\n"
    "  - Khi bật /ai hoặc gọi /gpt /grok /gemini, bot sẽ không thể trả lời theo model.\n"
    "  - Các lệnh AI hiện chỉ trả về thông báo bảo trì để tránh lỗi khi gọi dịch vụ bên ngoài.\n\n"
    "• *Bạn có thể làm gì bây giờ?*\n"
    "  - Sử dụng các công cụ khác của bot: /ip, /tiktok, /tiktokinfo.\n"
    "  - Nếu bạn là admin hoặc quản trị viên, liên hệ người quản lý bot để trao đổi việc kích hoạt lại.\n\n"
    "Cảm ơn bạn đã thông cảm — khi chức năng AI được bật trở lại, bot sẽ hoạt động bình thường.\n"
)

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    # gửi thông báo bảo trì dài
    await update.message.reply_text(append_footer(MAINT_MSG))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer("✅ Bạn đã thoát khỏi chế độ AI (nếu đang bật)."))

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
# 🚀 Start / Help (chi tiết)
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    await update.message.reply_text(append_footer(
        "✨ *Chào mừng bạn đến với BOT* ✨\n\n"
        "🤖 Công cụ chính:  \n"
        "  • 🌐 Kiểm tra IP (IP lookup)\n"
        "  • 🎬 Tải TikTok (video / ảnh)\n"
        "  • 📱 Lấy thông tin TikTok (nếu API có dữ liệu)\n"
        "  • 🔧 Chức năng AI: hiện đang bảo trì (xem /ai để biết chi tiết)\n\n"
        "📌 *Phát triển*: Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
    ))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    text = (
        "📖 *HƯỚNG DẪN SỬ DỤNG BOT* — CHI TIẾT\n\n"

        "1) Lệnh cơ bản\n"
        "   • /start — Hiển thị thông tin giới thiệu bot.\n"
        "   • /help — Hiển thị hướng dẫn chi tiết này.\n\n"

        "2) Chế độ AI (hiện tạm ngưng)\n"
        "   • /ai — Bật chế độ AI (nơi bạn chọn model và chat với model).\n"
        "   • /gpt — Chọn ChatGPT làm model.\n"
        "   • /grok — Chọn Grok làm model.\n"
        "   • /gemini — Chọn Gemini làm model.\n"
        "   • /exit — Thoát chế độ AI.\n\n"
        "   🔧 *Lưu ý về AI (bảo trì):*  \n"
        "   Hiện các lệnh AI được tạm dừng để bảo trì, cập nhật cấu hình và bảo mật. "
        "Khi chế độ AI được bật trở lại, thao tác sẽ như sau:  \n"
        "     1. Gõ /ai  \n"
        "     2. Gõ /gpt hoặc /grok hoặc /gemini để chọn model  \n"
        "     3. Nhập câu hỏi — bot sẽ trả lời bằng model bạn chọn.  \n"
        "   *Nếu bạn cần trả lời tức thời, sử dụng các công cụ khác của bot trong lúc này.*\n\n"

        "3) Công cụ IP\n"
        "   • /ip <địa_chỉ_ip> — Trả về thông tin về IP (quốc gia, thành phố, ISP, tọa độ, múi giờ...).\n"
        "     Ví dụ: `/ip 8.8.8.8`\n"
        "   • Ghi chú: lệnh này tra cứu từ dịch vụ bên thứ 3 (ip-api.com) — thông tin dựa trên cơ sở dữ liệu công khai.\n\n"

        "4) TikTok\n"
        "   • /tiktok <link> — Tải video hoặc ảnh từ link TikTok (chỉ cần cung cấp link, ví dụ: `/tiktok https://www.tiktok.com/@user/video/123`).\n"
        "     - Nếu là video: bot gửi video (nếu api hỗ trợ).  \n"
        "     - Nếu là album ảnh: bot gửi lần lượt các ảnh.\n"
        "   • /tiktokinfo <username> — Lấy thông tin tài khoản TikTok (nếu API trả dữ liệu).\n"
        "     Ví dụ: `/tiktokinfo username` (không cần @).  \n"
        "     Trả về: tên hiển thị, uid, verified (nếu có), followers, total likes, số video, bio, avatar (nếu có).\n\n"

        "5) Lệnh quản trị (chỉ dành cho admin @DuRinn_LeTuanDiem)\n"
        "   • /shutdown — Dừng bot hoàn toàn.\n"
        "   • /restart — Khởi động lại bot (server sẽ restart ngay lập tức).\n"
        "   • /startbot — Kiểm tra trạng thái bot (trả về tin nhắn xác nhận).\n\n"

        "6) Lưu ý & pháp lý\n"
        "   • Sử dụng công cụ một cách hợp pháp. Không lạm dụng để thu thập thông tin cá nhân mà không được phép.  \n"
        "   • Bot có thể bị giới hạn hoặc thay đổi hành vi nếu dịch vụ bên thứ ba thay đổi API.\n\n"
        "Nếu cần hỗ trợ thêm, liên hệ admin: @DuRinn_LeTuanDiem"
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
        await update.message.reply_text(append_footer("👉 Dùng: /ip 8.8.8.8"))
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
        user = requests.get(api_url, headers=HEADERS, timeout=15).json().get("data", {})
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
