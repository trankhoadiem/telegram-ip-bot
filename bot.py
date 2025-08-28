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
# Lưu ý: đặt biến môi trường trong Railway: TOKEN, OPENAI_API_KEY, XAI_API_KEY, GOOGLE_API_KEY
# Nếu bạn upload file OPENAI_API_KEY.txt / XAI_API_KEY.txt / GOOGLE_API_KEY.txt vào /mnt/data,
# code sẽ cố load từ đó nếu ENV không có.
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = os.environ.get("XAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")   # Gemini key

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

# -------------------
# logging
# -------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------
# helper: load from /mnt/data fallback if ENV missing
# -------------------
def _load_key_from_files(env_name: str, filenames: List[str]) -> Optional[str]:
    v = os.environ.get(env_name)
    if v:
        return v
    for fn in filenames:
        p = f"/mnt/data/{fn}"
        try:
            if os.path.exists(p):
                with open(p, "r") as f:
                    val = f.read().strip()
                    if val:
                        logger.info(f"Loaded {env_name} from {p}")
                        return val
        except Exception:
            pass
    return None

if not OPENAI_API_KEY:
    OPENAI_API_KEY = _load_key_from_files("OPENAI_API_KEY", ["OPENAI_API_KEY.txt", "OPENAI_KEY.txt", "OPENAI_API_KEY.TXT"])
if not XAI_API_KEY:
    XAI_API_KEY = _load_key_from_files("XAI_API_KEY", ["XAI_API_KEY.txt", "XAI_KEY.txt", "XAI_API_KEY.TXT"])
if not GOOGLE_API_KEY:
    GOOGLE_API_KEY = _load_key_from_files("GOOGLE_API_KEY", ["GOOGLE_API_KEY.txt", "GOOGLE_KEY.txt", "GOOGLE_API_KEY.TXT"])
if not TOKEN:
    TOKEN = _load_key_from_files("TOKEN", ["TOKEN.txt", "token.txt"])

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# -------------------
# delete helpers
# -------------------
async def delete_after_delay(context: ContextTypes.DEFAULT_TYPE, chat_id: int, msg_ids: List[int], delay: int = 300):
    """Xóa message ids sau `delay` giây (mặc định 300s = 5 phút)."""
    await asyncio.sleep(delay)
    for mid in msg_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception as e:
            logger.debug(f"Can't delete message {mid} in {chat_id}: {e}")

# -------------------
# API wrappers (đều gọi trong thread để ko block loop)
# -------------------
async def chat_gpt_async(query: str) -> str:
    if not OPENAI_API_KEY:
        return "❌ GPT lỗi: OPENAI_API_KEY chưa được đặt."
    try:
        openai.api_key = OPENAI_API_KEY
        def sync_call():
            return openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content":query}],
                timeout=30
            )
        resp = await asyncio.to_thread(sync_call)
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        logger.exception("OpenAI error")
        return f"⚠️ GPT lỗi: {e}"

async def chat_grok_async(query: str) -> str:
    if not XAI_API_KEY:
        return "❌ GROK lỗi: XAI_API_KEY chưa được đặt."
    try:
        def sync_call():
            url = "https://api.x.ai/v1/chat/completions"
            headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
            payload = {"model":"grok-2","messages":[{"role":"user","content":query}]}
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            r.raise_for_status()
            return r.json()
        data = await asyncio.to_thread(sync_call)
        # defensive
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            logger.debug("Unexpected grok response: %s", data)
            return f"⚠️ GROK trả về format lạ: {data}"
    except Exception as e:
        logger.exception("Grok error")
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
        logger.exception("Gemini error")
        return f"⚠️ GEMINI lỗi: {e}"

# -------------------
# Handlers
# -------------------

# 1) Xoá ngay tin nhắn user (không xoá lệnh /command). 
#    Filter: ALL & ~COMMAND để tránh xoá lệnh như /start, /clear.
async def auto_delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    try:
        await update.message.delete()
    except Exception as e:
        logger.debug("auto_delete_user: cannot delete user message: %s", e)

# 2) /clear admin: xóa lịch sử theo batch bằng chat.get_history()
async def clear_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        m = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        return

    chat = update.effective_chat
    chat_id = chat.id
    notice = await update.message.reply_text("🧹 Bắt đầu xóa tin nhắn (batch). Vui lòng chờ...")
    try:
        # kiểm tra quyền bot trong group
        try:
            me = await context.bot.get_me()
            if chat.type in ("group", "supergroup"):
                bot_member = await context.bot.get_chat_member(chat_id, me.id)
                can_delete = getattr(bot_member, "can_delete_messages", False)
                if not can_delete:
                    await notice.edit_text("❌ Bot cần quyền quản trị 'Delete messages' để xóa tin nhắn trong nhóm. Hãy promote bot và bật quyền.")
                    context.application.create_task(delete_after_delay(context, chat_id, [notice.message_id]))
                    return
        except Exception:
            logger.debug("Could not check bot admin status (ignored)")

        deleted = 0
        batches = 0
        # mỗi batch lấy tối đa 200 tin nhắn. Giới hạn batches để tránh loop vô hạn.
        while batches < 10:
            # lấy đối tượng Chat rồi duyệt history
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
                    # skip message we can't delete
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

# 3) /testapi để kiểm tra 3 key
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
            logger.exception("OpenAI test error")
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
            logger.exception("Grok test error")
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
            logger.exception("Gemini test error")
            return f"GEMINI: ⚠️ {e}"

    res = await asyncio.gather(check_openai(), check_grok(), check_gemini(), return_exceptions=False)
    await m.edit_text("🔎 Kết quả kiểm tra API:\n" + "\n".join(res) + "\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# 4) AI mode và model-select handlers
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    m = await update.message.reply_text(
        "🤖 Đã bật Chế độ AI\n"
        "Chọn model:\n/gpt  /grok  /gemini\n/exit để thoát\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    m = await update.message.reply_text("✅ Đã thoát AI mode.\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def set_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gpt"
    m = await update.message.reply_text("🧠 Chọn ChatGPT. Nhập nội dung để chat. (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def set_grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "grok"
    m = await update.message.reply_text("🦉 Chọn Grok. Nhập nội dung để chat. (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def set_gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gemini"
    m = await update.message.reply_text("🌌 Chọn Gemini. Nhập nội dung để chat. (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# 5) Xử lý tin nhắn khi ở AI mode (lưu text trước khi message có thể bị xóa)
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return

    if not update.message:
        return
    text = (update.message.text or "").strip()
    if not text:
        return
    thinking = await update.message.reply_text("⏳ Đang suy nghĩ...")
    # cố gắng xóa tin user (nếu chưa bị auto handler xóa)
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

    final = await thinking.edit_text(reply + "\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [final.message_id]))

# 6) start/help
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await update.message.reply_text(
        "✨ Chào mừng bạn đến với BOT\n\n"
        "Lệnh: /ai /gpt /grok /gemini /exit /testapi /clear\n"
        "Ghi chú: Tin nhắn user sẽ bị xóa NGAY. Tin nhắn bot sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await update.message.reply_text(
        "📖 Danh sách lệnh:\n"
        "/start /help /ai /gpt /grok /gemini /exit /testapi /clear\n\n"
        "⏳ Tin nhắn bot sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# -------------------
# main
# -------------------
def main():
    if not TOKEN:
        logger.error("TOKEN chưa được đặt. Đặt biến môi trường TOKEN hoặc upload TOKEN.txt vào /mnt/data.")
        sys.exit(1)

    app = Application.builder().token(TOKEN).build()

    # 1) auto delete user messages (non-command) - xử lý trước để xoá user ngay
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, auto_delete_user), group=0)

    # AI & command handlers
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("exit", exit_ai))
    app.add_handler(CommandHandler("gpt", set_gpt))
    app.add_handler(CommandHandler("grok", set_grok))
    app.add_handler(CommandHandler("gemini", set_gemini))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))

    # Tools / admin
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("testapi", testapi))
    app.add_handler(CommandHandler("clear", clear_chat))

    logger.info("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
