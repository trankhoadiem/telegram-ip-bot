# bot.py
# Requirements:
#   pip install python-telegram-bot==20.* openai requests google-generativeai
# Then run: python bot.py
import os
import sys
import asyncio
import logging
from typing import List, Optional

import requests
import openai
import google.generativeai as genai

from telegram import Update, Chat
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# --------------------------
# Logging
# --------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------
# Load config / keys
# --------------------------
def _load_key_from_files(env_name: str, alt_filenames: List[str]) -> Optional[str]:
    v = os.environ.get(env_name)
    if v:
        return v
    # try a few fallback filenames in /mnt/data (Railway uploads)
    for fname in alt_filenames:
        try:
            path = f"/mnt/data/{fname}"
            if os.path.exists(path):
                with open(path, "r") as f:
                    val = f.read().strip()
                    if val:
                        logger.info(f"Loaded {env_name} from {path}")
                        return val
        except Exception:
            pass
    return None

TOKEN = _load_key_from_files("TOKEN", ["TOKEN.txt", "token.txt"]) or os.environ.get("TOKEN")
OPENAI_API_KEY = _load_key_from_files("OPENAI_API_KEY", ["OPENAI_API_KEY.txt", "OPENAI_KEY.txt"]) or os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = _load_key_from_files("XAI_API_KEY", ["XAI_API_KEY.txt", "XAI_KEY.txt"]) or os.environ.get("XAI_API_KEY")
GOOGLE_API_KEY = _load_key_from_files("GOOGLE_API_KEY", ["GOOGLE_API_KEY.txt", "GOOGLE_KEY.txt"]) or os.environ.get("GOOGLE_API_KEY")

# Admin username (change if cần)
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin_user(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.username == ADMIN_USERNAME)

# --------------------------
# Utilities: delete after delay
# --------------------------
async def delete_after_delay(context: ContextTypes.DEFAULT_TYPE, chat_id: int, msg_ids: List[int], delay: int = 300):
    """Xóa các message ids sau `delay` giây (default 300s = 5 phút)."""
    await asyncio.sleep(delay)
    for mid in msg_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception as e:
            # không stop khi 1 message ko xóa được
            logger.debug(f"Failed to delete message {mid} in {chat_id}: {e}")

# --------------------------
# API wrappers (non-blocking from event loop)
# --------------------------
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
        content = resp["choices"][0]["message"]["content"]
        return content
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
            payload = {
                "model": "grok-2",
                "messages": [{"role": "user", "content": query}],
            }
            r = requests.post(url, headers=headers, json=payload, timeout=30)
            # raise for http errors
            r.raise_for_status()
            return r.json()

        data = await asyncio.to_thread(sync_call)
        # defensive parsing
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
            # resp may be an object with .text
            return getattr(resp, "text", str(resp))

        text = await asyncio.to_thread(sync_call)
        return text
    except Exception as e:
        logger.exception("Gemini call failed")
        return f"⚠️ GEMINI lỗi: {e}"

# --------------------------
# Handlers
# --------------------------

# 1) auto delete user message immediately (delete everything non-command)
async def auto_delete_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # xóa tin nhắn user ngay khi nhận (nếu có quyền)
    if not update.message:
        return
    try:
        await update.message.delete()
    except Exception as e:
        # không phải lỗi nghiêm trọng, log để debug
        logger.debug("Could not delete user message: %s", e)

# 2) /clear  -> delete old messages in chat (batch)
async def clear_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin_user(update):
        m = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))
        return

    chat = update.effective_chat
    chat_id = chat.id
    notice = await update.message.reply_text("🧹 Bắt đầu xóa tin nhắn (batch). Bot sẽ cố gắng xóa tối đa hàng nghìn tin nhắn...")
    # kiểm tra quyền (cho group/supergroup)
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
        # ignore check errors
        logger.debug("Could not check bot's admin status")

    deleted = 0
    try:
        # Duyệt nhiều batch (mỗi batch lấy 200 tin gần nhất)
        # Lưu ý: Telegram API/ptb có giới hạn, nên ta chỉ cố gắng xóa một số lớn nhưng không infinite loop.
        batches = 0
        while batches < 10:  # 10 * 200 = 2000 tin nhắn max
            msgs = []
            async for m in (await context.bot.get_chat(chat_id)).get_history(limit=200):
                msgs.append(m)
            if not msgs:
                break
            for m in msgs:
                try:
                    await context.bot.delete_message(chat_id=chat_id, message_id=m.message_id)
                    deleted += 1
                except Exception:
                    # skip failure
                    pass
            batches += 1
            # if less than batch size, we've reached the oldest available
            if len(msgs) < 200:
                break
        done = await update.message.reply_text(f"✅ Xong. Đã cố gắng xóa ~{deleted} tin nhắn (trong giới hạn batch).")
        context.application.create_task(delete_after_delay(context, chat_id, [notice.message_id, done.message_id]))
    except Exception as e:
        logger.exception("Error during clear")
        errm = await update.message.reply_text(f"⚠️ Lỗi khi xóa: {e}")
        context.application.create_task(delete_after_delay(context, chat_id, [notice.message_id, errm.message_id]))

# 3) /testapi -> kiểm tra 3 key nhanh
async def testapi_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("🔎 Kiểm tra API keys...")
    results = []
    # run tests in parallel
    async def test_openai():
        if not OPENAI_API_KEY:
            return "OPENAI: ❌ missing"
        try:
            def sync_check():
                openai.api_key = OPENAI_API_KEY
                # nhẹ: request danh sách model (may raise if auth fails)
                return openai.Model.list()
            resp = await asyncio.to_thread(sync_check)
            return "OPENAI: ✅ OK"
        except Exception as e:
            logger.exception("OpenAI test failed")
            return f"OPENAI: ⚠️ {e}"

    async def test_grok():
        if not XAI_API_KEY:
            return "GROK: ❌ missing"
        try:
            def sync_check():
                url = "https://api.x.ai/v1/models"
                headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
                r = requests.get(url, headers=headers, timeout=15)
                r.raise_for_status()
                return r.json()
            await asyncio.to_thread(sync_check)
            return "GROK: ✅ OK"
        except Exception as e:
            logger.exception("Grok test failed")
            return f"GROK: ⚠️ {e}"

    async def test_gemini():
        if not GOOGLE_API_KEY:
            return "GEMINI: ❌ missing"
        try:
            def sync_check():
                genai.configure(api_key=GOOGLE_API_KEY)
                # thử create 1 token nhỏ
                model = genai.GenerativeModel("gemini-1.5-small")
                resp = model.generate_content("Hello")
                return getattr(resp, "text", str(resp))
            await asyncio.to_thread(sync_check)
            return "GEMINI: ✅ OK"
        except Exception as e:
            logger.exception("Gemini test failed")
            return f"GEMINI: ⚠️ {e}"

    res = await asyncio.gather(test_openai(), test_grok(), test_gemini(), return_exceptions=False)
    await msg.edit_text("🔎 Kết quả kiểm tra API:\n" + "\n".join(res) + "\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))

# 4) AI mode command + simple per-model commands
async def ai_mode_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    m = await update.message.reply_text(
        "🤖 Chế độ AI: Chọn model:\n"
        "/gpt (ChatGPT)  /grok (Grok)  /gemini (Gemini)\n"
        "/exit để thoát.\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def exit_ai_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = None
    m = await update.message.reply_text("✅ Đã thoát AI mode.\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def set_gpt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gpt"
    m = await update.message.reply_text("🧠 Đã chuyển sang ChatGPT. Gõ nội dung để chat. (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def set_grok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "grok"
    m = await update.message.reply_text("🦉 Đã chuyển sang Grok. Gõ nội dung để chat. (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def set_gemini_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["ai_mode"] = "gemini"
    m = await update.message.reply_text("🌌 Đã chuyển sang Gemini. Gõ nội dung để chat. (/exit để thoát)\n\n⏳ Tin nhắn sẽ tự động xóa sau 5 phút.")
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# 5) handle plain text when in ai_mode
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return  # not in ai mode

    # keep a copy of content (update.message might be deleted by auto_delete_user handler)
    text = (update.message.text or "").strip()
    if not text:
        return
    thinking = await update.message.reply_text("⏳ Đang suy nghĩ...")
    # ensure user message deleted (try again, if it wasn't already)
    try:
        await update.message.delete()
    except Exception:
        pass

    # call appropriate API wrapper
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

# 6) Simple /start and /help
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await update.message.reply_text(
        "✨ Chào! Bot đã hoạt động.\n"
        "Lệnh chính: /ai /gpt /grok /gemini /exit /testapi /clear\n\n"
        "⏳ Tin nhắn bot sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = await update.message.reply_text(
        "📖 Danh sách lệnh:\n"
        "/start - bắt đầu\n"
        "/ai - vào chế độ AI\n"
        "/gpt - chuyển model sang ChatGPT\n"
        "/grok - chuyển sang Grok\n"
        "/gemini - chuyển sang Gemini\n"
        "/exit - thoát AI mode\n"
        "/testapi - kiểm tra API keys\n"
        "/clear - xóa tin nhắn cũ (admin)\n\n"
        "Ghi chú: Tin nhắn user bị xóa NGAY. Tin nhắn bot sẽ tự động xóa sau 5 phút."
    )
    context.application.create_task(delete_after_delay(context, update.effective_chat.id, [m.message_id]))

# --------------------------
# Main
# --------------------------
def main():
    if not TOKEN:
        logger.error("TOKEN chưa được đặt. Đặt biến NODE 'TOKEN' trong Railway.")
        sys.exit(1)

    app = Application.builder().token(TOKEN).build()

    # order: register auto-delete user handler FIRST so user messages are removed asap
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, auto_delete_user_handler), group=0)

    # AI & plain message handlers
    app.add_handler(CommandHandler("ai", ai_mode_handler))
    app.add_handler(CommandHandler("exit", exit_ai_handler))
    app.add_handler(CommandHandler("gpt", set_gpt_handler))
    app.add_handler(CommandHandler("grok", set_grok_handler))
    app.add_handler(CommandHandler("gemini", set_gemini_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))

    # Tools + admin
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("testapi", testapi_handler))
    app.add_handler(CommandHandler("clear", clear_chat_handler))

    # run
    logger.info("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
