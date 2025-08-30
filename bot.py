# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import requests, os, sys, asyncio

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

# ==== Auto delete helper ====
async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except:
        pass

async def auto_delete(msg, delay=15):
    try:
        await asyncio.sleep(delay)
        await msg.delete()
    except:
        pass

# ==== Đa ngôn ngữ ====
user_lang = {}  # user_id -> "vi"|"en"|"ru"

LANGS = {
    "vi": {
        "start": "✨ *Chào mừng bạn đến với BOT* ✨\n\n"
                 "🤖 Công cụ chính:\n"
                 "  • 🌐 Kiểm tra thông tin IP\n"
                 "  • 🎬 Tải video/ảnh từ TikTok\n"
                 "  • 📱 Lấy thông tin tài khoản TikTok\n"
                 "  • 🔧 AI (hiện đang bảo trì)\n\n"
                 "📌 *Phát triển*: Tô Minh Điềm – @DuRinn_LeTuanDiem",

        "help": "📖 *HƯỚNG DẪN CÁC LỆNH*\n\n"
                "1) /start — Lời chào & thông tin bot.\n"
                "2) /help — Danh sách lệnh.\n"
                "3) /ip <địa_chỉ_ip> — Xem thông tin IP.\n"
                "4) /tiktok <link> — Tải video/ảnh TikTok.\n"
                "5) /tiktokinfo <username> — Lấy info TikTok.\n"
                "6) /shutdown, /restart, /startbot — Quản trị (admin).",

        "ai_maint": "🔧 *Chức năng AI hiện đang bảo trì & nâng cấp*\n\n"
                    "Các model AI như ChatGPT, Grok, Gemini tạm thời không hoạt động.\n\n"
                    "📌 Bạn vẫn có thể dùng: /ip, /tiktok, /tiktokinfo.",

        "lang_changed": "✅ Đã đổi ngôn ngữ sang *Tiếng Việt* 🇻🇳"
    },
    "en": {
        "start": "✨ *Welcome to the BOT* ✨\n\n"
                 "🤖 Main tools:\n"
                 "  • 🌐 Check IP information\n"
                 "  • 🎬 Download TikTok videos/photos\n"
                 "  • 📱 Get TikTok account info\n"
                 "  • 🔧 AI (currently under maintenance)\n\n"
                 "📌 *Developer*: To Minh Diem – @DuRinn_LeTuanDiem",

        "help": "📖 *BOT COMMANDS*\n\n"
                "1) /start — Show welcome info.\n"
                "2) /help — List of commands.\n"
                "3) /ip <ip_address> — Get IP details.\n"
                "4) /tiktok <link> — Download TikTok videos/photos.\n"
                "5) /tiktokinfo <username> — Get TikTok user info.\n"
                "6) /shutdown, /restart, /startbot — Admin only.",

        "ai_maint": "🔧 *AI functions are under maintenance & upgrade*\n\n"
                    "Models like ChatGPT, Grok, Gemini are temporarily unavailable.\n\n"
                    "📌 You can still use: /ip, /tiktok, /tiktokinfo.",

        "lang_changed": "✅ Language switched to *English (US)* 🇺🇸"
    },
    "ru": {
        "start": "✨ *Добро пожаловать в BOT* ✨\n\n"
                 "🤖 Основные функции:\n"
                 "  • 🌐 Проверка информации об IP\n"
                 "  • 🎬 Загрузка видео/фото из TikTok\n"
                 "  • 📱 Информация об аккаунте TikTok\n"
                 "  • 🔧 AI (временно недоступен)\n\n"
                 "📌 *Разработчик*: To Minh Diem – @DuRinn_LeTuanDiem",

        "help": "📖 *КОМАНДЫ БОТА*\n\n"
                "1) /start — Приветствие и информация.\n"
                "2) /help — Список команд.\n"
                "3) /ip <ip_address> — Проверка IP.\n"
                "4) /tiktok <ссылка> — Скачать TikTok видео/фото.\n"
                "5) /tiktokinfo <username> — Инфо TikTok аккаунта.\n"
                "6) /shutdown, /restart, /startbot — Только админ.",

        "ai_maint": "🔧 *Функции AI находятся на обслуживании*\n\n"
                    "Модели ChatGPT, Grok, Gemini временно недоступны.\n\n"
                    "📌 Доступны команды: /ip, /tiktok, /tiktokinfo.",

        "lang_changed": "✅ Язык изменён на *Русский* 🇷🇺"
    }
}

def get_lang(update: Update):
    uid = update.effective_user.id
    return user_lang.get(uid, "vi")  # mặc định: tiếng Việt

def get_text(update: Update, key: str):
    return LANGS[get_lang(update)][key]

# ==== Lệnh đổi ngôn ngữ ====
async def set_lang_vi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang[update.effective_user.id] = "vi"
    msg = await update.message.reply_text(LANGS["vi"]["lang_changed"])
    asyncio.create_task(auto_delete(msg))

async def set_lang_en(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang[update.effective_user.id] = "en"
    msg = await update.message.reply_text(LANGS["en"]["lang_changed"])
    asyncio.create_task(auto_delete(msg))

async def set_lang_ru(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_lang[update.effective_user.id] = "ru"
    msg = await update.message.reply_text(LANGS["ru"]["lang_changed"])
    asyncio.create_task(auto_delete(msg))

# =======================
# 🔧 AI MODE
# =======================
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(get_text(update, "ai_maint"))
    asyncio.create_task(auto_delete(msg))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text("✅ Exit AI mode.")
    asyncio.create_task(auto_delete(msg))

async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ai_mode(update, context)

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ai_mode(update, context)

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ai_mode(update, context)

# =======================
# 🔒 Admin commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Permission denied.")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("🛑 Shutting down...")
    asyncio.create_task(auto_delete(msg))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Permission denied.")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("♻️ Restarting bot...")
    asyncio.create_task(auto_delete(msg))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Permission denied.")
        asyncio.create_task(auto_delete(msg))
        return
    msg = await update.message.reply_text("✅ Bot is running normally!")
    asyncio.create_task(auto_delete(msg))

# =======================
# 🚀 Start / Help
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(get_text(update, "start"))
    asyncio.create_task(auto_delete(msg))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text(get_text(update, "help"))
    asyncio.create_task(auto_delete(msg, delay=30))

# =======================
# 🌐 IP checker
# =======================
def get_ip_info(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        res = requests.get(url, timeout=15).json()
        if res.get("status") == "fail":
            return None, f"❌ Invalid IP: {ip}"
        info = (
            f"🌐 IP {res['query']}:\n"
            f"🏳️ {res['country']} ({res['countryCode']})\n"
            f"🏙 {res['regionName']} - {res['city']} ({res.get('zip','')})\n"
            f"🕒 {res['timezone']}\n"
            f"📍 {res['lat']}, {res['lon']}\n"
            f"📡 ISP: {res['isp']}\n"
            f"🏢 Org: {res['org']}\n"
            f"🔗 AS: {res['as']}"
        )
        return f"https://flagcdn.com/w320/{res['countryCode'].lower()}.png", info
    except Exception as e:
        return None, f"⚠️ Error: {e}"

async def check_ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Usage: /ip <address>")
        asyncio.create_task(auto_delete(msg))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        msg = await update.message.reply_photo(flag_url, caption=info)
    else:
        msg = await update.message.reply_text(info)
    asyncio.create_task(auto_delete(msg))

# =======================
# 🎬 TikTok
# =======================
async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Usage: /tiktok <link>")
        asyncio.create_task(auto_delete(msg))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Processing TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20).json()
        if res.get("code") != 0 or "data" not in res:
            await waiting_msg.edit_text("❌ Failed to download.")
            asyncio.create_task(auto_delete(waiting_msg))
            return
        data = res["data"]
        title = data.get("title", "TikTok")
        await waiting_msg.delete()
        if data.get("hdplay") or data.get("play"):
            msg = await update.message.reply_video(data.get("hdplay") or data.get("play"),
                                                   caption=f"🎬 {title}")
            asyncio.create_task(auto_delete(msg))
        elif data.get("images"):
            for img in data["images"]:
                msg = await update.message.reply_photo(img)
                asyncio.create_task(auto_delete(msg))
        else:
            msg = await update.message.reply_text("⚠️ No video/photo found.")
            asyncio.create_task(auto_delete(msg))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Error: {e}")
        asyncio.create_task(auto_delete(waiting_msg))

async def tiktok_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not context.args:
        msg = await update.message.reply_text("👉 Usage: /tiktokinfo <username>")
        asyncio.create_task(auto_delete(msg))
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Fetching info @{username}...")
    try:
        api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
        user = requests.get(api_url, headers=HEADERS, timeout=15).json().get("data", {})
        caption = (
            f"📱 TikTok @{user.get('unique_id', username)}\n"
            f"👤 {user.get('nickname','N/A')}\n"
            f"🌍 {user.get('region','?')}\n"
            f"👥 Followers: {user.get('follower_count','?')}\n"
            f"❤️ Likes: {user.get('total_favorited','?')}\n"
            f"🎬 Videos: {user.get('aweme_count','?')}\n"
            f"📝 Bio: {user.get('signature','')}"
        )
        avatar = user.get("avatar")
        await waiting_msg.delete()
        if avatar:
            msg = await update.message.reply_photo(avatar, caption=caption)
        else:
            msg = await update.message.reply_text(caption)
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Error: {e}")
        asyncio.create_task(auto_delete(waiting_msg))

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

    # Language
    app.add_handler(CommandHandler("vi-vn", set_lang_vi))
    app.add_handler(CommandHandler("en-us", set_lang_en))
    app.add_handler(CommandHandler("ru", set_lang_ru))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()