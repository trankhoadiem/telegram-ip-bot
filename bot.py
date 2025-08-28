# bot.py
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import sys
import openai
import google.generativeai as genai
import asyncio
import logging
from typing import List, Optional

# ==== TOKEN & API KEYS ====
# Railway/Heroku: set Service Variables: TOKEN, OPENAI_API_KEY, XAI_API_KEY, GOOGLE_API_KEY
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = os.environ.get("XAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")   # Gemini key

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.tikwm.com/"}

# -------------------
# logging
# -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------
# Fallback: try load keys from /mnt/data if ENV not set (useful for dev)
# -------------------
def _load_key_from_files(env_name: str, filenames: List[str]) -> Optional[str]:
    v = os.environ.get(env_name)
    if v:
        return v
    for fn in filenames:
        p = f"/mnt/data/{fn}"
        try:
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    val = f.read().strip()
                    if val:
                        logger.info(f"Loaded {env_name} from {p}")
                        return val
        except Exception:
            pass
    return None

if not OPENAI_API_KEY:
    OPENAI_API_KEY = _load_key_from_files("OPENAI_API_KEY", ["OPENAI_API_KEY.txt", "OPENAI_KEY.txt"])
if not XAI_API_KEY:
    XAI_API_KEY = _load_key_from_files("XAI_API_KEY", ["XAI_API_KEY.txt", "XAI_KEY.txt"])
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = _load_key_from_files("GOOGLE_API_KEY", ["GOOGLE_API_KEY.txt", "GOOGLE_KEY.txt"])
if not TOKEN:
    TOKEN = _load_key_from_files("TOKEN", ["TOKEN.txt", "token.txt"])

# Log presence (do not print actual keys)
logger.info("ENV keys presence: OPENAI=%s XAI=%s GOOGLE=%s TOKEN=%s",
            bool(OPENAI_API_KEY), bool(XAI_API_KEY), bool(GOOGLE_API_KEY), bool(TOKEN))

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# -------------------
# delete helpers
# -------------------
async def delete_after_delay(context: ContextTypes.DEFAULT_TYPE, chat_id: int, msg_ids: List[int], delay: int = 300):
    """Xóa các message ids sau `delay` giây (mặc định 300s = 5 phút)."""
    await asyncio.sleep(delay)
    for mid in msg_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception as e:
            logger.debug("Failed delete message %s in %s: %s", mid, chat_id, e)

# -------------------
# API wrappers (non-blocking using to_thread)
# -------------------
async def chat_gpt_async(query: str) -> str:
    if not OPENAI_API_KEY:
        return "❌ GPT lỗi: OPENAI_API_KEY chưa được đặt."
    try:
        openai.api_key = OPENAI_API_KEY
        def sync_call():
            return openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": query}],
                timeout=30,
            )
        resp = await asyncio.to_thread(sync_call)
        # defensive parse
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        logger.exception("OpenAI call failed")
        return f"⚠️ GPT lỗi: {e}"

async def chat_grok_async(query: str) -> str:
    if not XAI_API_KEY:
        return "❌ GROK lỗi: XAI_API_KEY chưa được đặt."
    try:
        def sync_call():
            url = "https://api.x.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
            payload = {"model": "grok-2", "messages": [{"role": "user", "content": query}]}
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            return r.json()
        data = await asyncio.to_thread(sync_call)
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            logger.debug("Unexpected Grok response: %s", data)
            return f"⚠️ GROK trả về format lạ: {data}"
    except Exception as e:
        logger.exception("Grok call failed")
        return f"⚠️ GROK lỗi: {e}"

async def chat_gemini_async(query: str) -> str:
    if not GOOGLE_API_KEY:
        return "❌ GEMINI lỗi: GOOGLE_API_KEY chưa được đặt."
    try:
        def sync_call():
            genai.configure(api_key=GOOGLE_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(query)
            return getattr(resp, "text", str(resp))
        text = await asyncio.to_thread(sync_call)
        return text
    except Exception as e:
        logger.exception("Gemini call failed")
        return f"⚠️ GEMINI lỗi: {e}"

# -------------------
# Handlers
# -------------------

# 1) auto-delete user messages immediately (non-command)
async def auto_delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    # We exclude commands by registering filter ~filters.COMMAND
    try:
        await update.message.delete()
    except Exception as e:
        logger.debug("auto_delete_user: cannot delete user message: %s", e)

# 2) /clear - admin only, batch delete history
async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        m = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        return

    chat = update.effective_chat
    chat_id = chat.id
    notice = await update.message.reply_text("🧹 Bắt đầu xóa tin nhắn (batch). Vui lòng chờ...")
    try:
        # check bot permissions if group
        try:
            me = await context.bot.get_me()
            if chat.type in ("group", "supergroup"):
                bot_member = await context.bot.get_chat_member(chat_id, me.id)
                can_delete = getattr(bot_member, "can_delete_messages", False)
                if not can_delete:
                    await notice.edit_text("❌ Bot cần quyền 'Delete messages' để xóa tin nhắn trong nhóm. Promote bot và bật quyền.")
                    context.application.create_task(delete_after_delay(context, chat_id, [notice.message_id]))
                    return
        except Exception:
            logger.debug("Could not check bot admin status (ignored)")

        deleted = 0
        batches = 0
        # limit batches to avoid infinite loop (10 * 200 = 2000 messages)
        while batches < 10:
            chat_obj = await context.bot.get_chat(chat_id)
            msgs = []
            async for m in chat_obj.get_history(limit=200):
                msgs.append(m)
            if not msgs:
                break
            for m in msgs:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=m.message_id)
                    deleted += 1
                except Exception:
                    pass
            batches += 1
            if len(msgs) < 200:
                break

        done = await update.message.reply_text(f"✅ Hoàn tất: đã cố gắng xóa ~{deleted} tin nhắn (batch giới hạn).")
        context.application.create_task(delete_after_delay(context, chat_id, [notice.message_id, done.message_id]))
    except Exception as e:
        logger.exception("clear_chat error")
        errm = await update.message.reply_text(f"⚠️ Lỗi khi xóa: {e}")
        context.application.create_task(delete_after_delay(context, chat_id, [notice.message_id, errm.message_id]))

# 3) /testapi -> kiểm tra 3 key (returns simple OK or error)
async def testapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await update.message.reply_text("🔎 Đang kiểm tra API keys...")
    async def check_openai():
        if not OPENAI_API_KEY:
            return "OPENAI: ❌ missing"
        try:
            def sync():
                openai.api_key = OPENAI_API_KEY
                return openai.Model.list()
            await asyncio.to_thread(sync)
            return "OPENAI: ✅ OK"
        except Exception as e:
            logger.exception("OpenAI test failed")
            return f"OPENAI: ⚠️ {e}"

    async def check_grok():
        if not XAI_API_KEY:
            return "GROK: ❌ missing"
        try:
            def sync():
                url = "https://api.x.ai/v1/models"
                headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
                r = requests.get(url, headers=headers, timeout=15)
                r.raise_for_status()
                return r.json()
            await asyncio.to_thread(sync)
            return "GROK: ✅ OK"
        except Exception as e:
            logger.exception("Grok test failed")
            return f"GROK: ⚠️ {e}"

    async def check_gemini():
        if not GOOGLE_API_KEY:
            return "GEMINI: ❌ missing"
        try:
            def sync():
                genai.configure(api_key=GOOGLE_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-small")
                resp = model.generate_content("Hello")
                return getattr(resp, "text", str(resp))
            await asyncio.to_thread(sync)
            return "GEMINI: ✅ OK"
        except Exception as e:
            logger.exception("Gemini test failed")
            return f"GEMINI: ⚠️ {e}"

    res = await asyncio.gather(check_openai(), check_grok(), check_gemini(), return_exceptions=False)
    await m.edit_text("🔎 Kết quả kiểm tra API:\n" + "\n".join(res) + "\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# 4) AI mode + select model
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    m = await update.message.reply_text(
        "🤖 Đã bật **Chế độ AI**\n\n"
        "👉 Chọn model để trò chuyện:\n"
        "/gpt - ChatGPT\n"
        "/grok - Grok\n"
        "/gemini - Gemini\n"
        "/exit - Thoát chế độ AI\n\n"
        "⏳ Tin nhắn sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    m = await update.message.reply_text("✅ Bạn đã thoát khỏi **Chế độ AI**.\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def gpt_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gpt"
    m = await update.message.reply_text("🧠 Bạn đang trò chuyện với **ChatGPT**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def grok_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "grok"
    m = await update.message.reply_text("🦉 Bạn đang trò chuyện với **Grok**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def gemini_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gemini"
    m = await update.message.reply_text("🌌 Bạn đang trò chuyện với **Gemini**. Hãy nhập tin nhắn... (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# 5) handle text when in AI mode
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return
    if not update.message:
        return
    text = (update.message.text or "").strip()
    if not text:
        return

    thinking_msg = await update.message.reply_text("⏳ Đang suy nghĩ...")
    # try delete user message (may already be deleted by auto_delete_user)
    try:
        await update.message.delete()
    except Exception:
        pass

    if mode == "gpt":
        reply = await chat_gpt_async(text)
    elif mode == "grok":
        reply = await chat_grok_async(text)
    elif mode == "gemini":
        reply = await chat_gemini_async(text)
    else:
        reply = "⚠️ Chưa chọn model AI."

    final = await thinking_msg.edit_text(reply + "\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [final.message_id]))

# 6) other commands (start/help/ip/tiktok/welcome) - keep original content but bot messages auto-delete
async def start(update, context):
    m = await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini)\n\n"
        "⚡ Bot vẫn đang **cập nhật hằng ngày**, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng.\n\n"
        "⏳ Tin nhắn sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def help_command(update, context):
    m = await update.message.reply_text(
        "📖 **Danh sách lệnh khả dụng**:\n\n"
        "🚀 /start - Bắt đầu\n"
        "🛠 /help - Trợ giúp\n"
        "🤖 /ai - Bật Chế độ AI (GPT, Grok, Gemini)\n"
        "🌐 /ip <ip> - Kiểm tra IP\n"
        "🎬 /tiktok <link> - Tải TikTok\n\n"
        "🔒 **Lệnh Admin** (@DuRinn_LeTuanDiem):\n"
        "🛑 /shutdown - Tắt bot\n"
        "♻️ /restart - Khởi động lại bot\n"
        "✅ /startbot - Kiểm tra bot\n"
        "🧹 /clear - Xoá toàn bộ tin nhắn cũ\n\n"
        "⏳ Tin nhắn sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

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

async def check_ip(update, context):
    if not context.args:
        m = await update.message.reply_text("👉 Dùng: /ip 8.8.8.8\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        m = await update.message.reply_photo(flag_url, caption=info + "\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
    else:
        m = await update.message.reply_text(info + "\n\n⏳ Tin nhắn sẽ tự động xoá sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def download_tiktok(update, context):
    if not context.args:
        m = await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20)
        data_json = res.json()
        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text("❌ Không tải được TikTok. Vui lòng kiểm tra lại link!\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
            context.application.create_task(delete_after_delay(context, update.effective_chat.id, [waiting_msg.message_id]))
            return
        data = data_json["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            m = await update.message.reply_video(url, caption=f"🎬 {title} (HQ)\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
            context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh...")
            for img_url in data["images"]:
                mm = await update.message.reply_photo(img_url, caption="⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
                context.application.create_task(delete_after_delay(context, update.effective_chat.id, [mm.message_id]))
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
            context.application.create_task(delete_after_delay(context, update.effective_chat.id, [waiting_msg.message_id]))
            return
    except Exception as e:
        logger.exception("download_tiktok error")
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [waiting_msg.message_id]))

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        m = await update.message.reply_text(
            f"🎉👋 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút."
        )
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# Admin commands
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        m = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        return
    m = await update.message.reply_text("🛑 Bot đang **tắt**...")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        m = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        return
    m = await update.message.reply_text("♻️ Bot đang **khởi động lại**...")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        m = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        return
    m = await update.message.reply_text("✅ Bot đang chạy bình thường!\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# -------------------
# MAIN
# -------------------
def main():
    if not TOKEN:
        logger.error("TOKEN chưa được đặt. Đặt biến môi trường TOKEN hoặc upload TOKEN.txt vào /mnt/data.")
        sys.exit(1)

    app = Application.builder().token(TOKEN).build()

    # register auto-delete user messages first (non-command) so they get removed asap
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, auto_delete_user), group=0)

    # AI handlers
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("exit", exit_ai))
    app.add_handler(CommandHandler("gpt", gpt_cmd))
    app.add_handler(CommandHandler("grok", grok_cmd))
    app.add_handler(CommandHandler("gemini", gemini_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))

    # Tools + admin
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("testapi", testapi))
    app.add_handler(CommandHandler("clear", clear_chat))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))

    # welcome
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    logger.info("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
