# bot.py
from telegram import Update, ReplyKeyboardMarkup, ChatMember, ChatPermissions
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
import requests, os, sys, asyncio
from datetime import datetime, timedelta
import yt_dlp

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

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
        pass

async def auto_delete(msg, delay=30):
    """Xóa tin nhắn bot sau delay giây"""
    try:
        await asyncio.sleep(delay)
        await msg.delete()
    except:
        pass

# =======================
# 🔧 AI MODE
# =======================
MAINT_MSG = (
    "🛠 *Chức năng AI đang bảo trì*\n\n"
    "Các model ChatGPT, Grok, Gemini tạm thời không hoạt động.\n"
    "📌 Bạn vẫn có thể dùng: /ip, /tiktok, /tiktokinfo, /youtube, /youtubeinfo."
)

async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text("✅ Đã thoát AI\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(MAINT_MSG + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

# =======================
# 🔒 Admin commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("🛑 Bot đang tắt...\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("♻️ Bot đang khởi động lại...\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("✅ Bot đang chạy bình thường!\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg))

# =======================
# 🚀 Start / Help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    keyboard = [["/help", "/kick", "/ban", "/mute", "/unmute"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    msg = await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "⚡ Bot cập nhật hằng ngày, ổn định và chuyên nghiệp.\n"
        "📌 Phát triển bởi: Tô Minh Điềm – @DuRinn_LeTuanDiem\n"
        "💡 Gõ /help để xem hướng dẫn chi tiết.\n\n"
        "⏳ Tin nhắn này sẽ tự động xoá sau 30 giây",
        reply_markup=reply_markup
    )
    asyncio.create_task(auto_delete(msg))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    keyboard = [["/start"], ["/ip", "/tiktok", "/youtube"], ["/tiktokinfo", "/youtubeinfo"], ["/ai", "/gpt", "/grok", "/gemini", "/exit"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    text = (
        "📖 *Hướng dẫn sử dụng BOT* (chi tiết)\n\n"
        "🚀 Lệnh cơ bản:\n"
        "  • /start — Giới thiệu bot.\n"
        "  • /help — Hiển thị hướng dẫn chi tiết.\n\n"
        "🌐 Công cụ IP:\n"
        "  • /ip <ip> — Xem thông tin IP.\n\n"
        "🎬 Công cụ TikTok:\n"
        "  • /tiktok <link> — Tải video/ảnh TikTok.\n"
        "  • /tiktokinfo <username> — Lấy info TikTok.\n\n"
        "🎥 Công cụ YouTube:\n"
        "  • /youtube <link> hoặc /yt <link> — Tải video YouTube (tự xoá sau 1 phút).\n"
        "  • /youtubeinfo <link> hoặc /ytinfo <link> — Xem thông tin video YouTube (tự xoá sau 1 phút).\n\n"
        "🤖 Chế độ AI (bảo trì):\n"
        "  • /ai, /gpt, /grok, /gemini, /exit\n\n"
        "🔒 Lệnh Admin:\n"
        "  • /shutdown, /restart, /startbot, /kick, /ban, /mute, /unmute (chỉ admin)\n\n"
        "⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
    )
    msg = await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    asyncio.create_task(auto_delete(msg, 30))

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
        msg = await update.message.reply_text("/ip <ip> để kiểm tra thông tin IP\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg, 30))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        msg = await update.message.reply_photo(flag_url, caption=info + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    else:
        msg = await update.message.reply_text(info + "\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
    asyncio.create_task(auto_delete(msg, 30))

# =======================
# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("/tiktok <link> để tải video/ảnh TikTok\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg, 30))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Không tải được TikTok\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
            asyncio.create_task(auto_delete(waiting_msg, 30))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        await waiting_msg.delete()
        if data.get("hdplay") or data.get("play"):
            msg = await update.message.reply_video(
                data.get("hdplay") or data.get("play"),
                caption=f"🎬 {title}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
            )
            asyncio.create_task(auto_delete(msg, 30))
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
                asyncio.create_task(auto_delete(msg, 30))
        else:
            msg = await update.message.reply_text("⚠️ Không tìm thấy video/ảnh\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
            asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok: {e}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(waiting_msg, 30))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("/tiktokinfo <username> để lấy info TikTok\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(msg, 30))
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
            f"📝 Bio: {user.get('signature','')}\n"
            f"⏳ Tin nhắn này sẽ tự động xoá sau 30 giây"
        )
        avatar = user.get("avatar")
        await waiting_msg.delete()
        if avatar:
            msg = await update.message.reply_photo(avatar, caption=caption)
        else:
            msg = await update.message.reply_text(caption)
        asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi TikTok info: {e}\n⏳ Tin nhắn này sẽ tự động xoá sau 30 giây")
        asyncio.create_task(auto_delete(waiting_msg, 30))

# =======================
# 🎬 YouTube
# =======================
async def youtube_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("/youtube <link> để tải video YouTube\n⏳ Tin nhắn này sẽ tự động xoá sau 1 phút")
        asyncio.create_task(auto_delete(msg, 60))
        return
    
    url = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý YouTube...")

    try:
        ydl_opts = {"format": "best[ext=mp4]/best", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info["url"]
            title = info.get("title", "YouTube Video")

        await waiting_msg.delete()
        msg = await update.message.reply_video(
            video_url,
            caption=f"🎬 {title}\n⏳ Tin nhắn này sẽ tự động xoá sau 1 phút"
        )
        asyncio.create_task(auto_delete(msg, 60))

    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi YouTube: {e}\n⏳ Tin nhắn này sẽ tự động xoá sau 1 phút")
        asyncio.create_task(auto_delete(waiting_msg, 60))


async def youtube_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("/youtubeinfo <link> để xem thông tin video YouTube\n⏳ Tin nhắn này sẽ tự động xoá sau 1 phút")
        asyncio.create_task(auto_delete(msg, 60))
        return
    
    url = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang lấy thông tin video...")

    try:
        ydl_opts = {"quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        caption = (
            f"🎬 *{info.get('title','N/A')}*\n"
            f"📺 Kênh: {info.get('uploader','?')}\n"
            f"👁 Views: {info.get('view_count','?')}\n"
            f"👍 Likes: {info.get('like_count','?')}\n"
            f"🕒 Thời lượng: {info.get('duration','?')} giây\n"
            f"📅 Ngày đăng: {info.get('upload_date','?')}\n"
            f"🔗 Link: {info.get('webpage_url','?')}\n"
            f"⏳ Tin nhắn này sẽ tự động xoá sau 1 phút"
        )

        await waiting_msg.delete()
        thumb = info.get("thumbnail")
        if thumb:
            msg = await update.message.reply_photo(thumb, caption=caption, parse_mode="Markdown")
        else:
            msg = await update.message.reply_text(caption, parse_mode="Markdown")
        asyncio.create_task(auto_delete(msg, 60))

    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi YouTube info: {e}\n⏳ Tin nhắn này sẽ tự động xoá sau 1 phút")
        asyncio.create_task(auto_delete(waiting_msg, 60))

# =======================
# 🎉 Chào người mới
# =======================
async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_member = update.chat_member
    new_user = chat_member.new_chat_member.user

    if chat_member.old_chat_member.status in ["left", "kicked"] and chat_member.new_chat_member.status == "member":
        keyboard = [["/start", "/kick", "/ban", "/mute", "/unmute"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        msg = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                f"✨ Chào mừng {new_user.mention_html()} đến với nhóm! ✨\n\n"
               
