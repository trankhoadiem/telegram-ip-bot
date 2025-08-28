# ==== AI HANDLERS ====
import openai
import requests
import google.generativeai as genai

# GPT
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not OPENAI_API_KEY:
        msg = await update.message.reply_text("❌ GPT lỗi: Chưa có API_KEY")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
        return
    try:
        openai.api_key = OPENAI_API_KEY
        question = " ".join(context.args) if context.args else "Hello"
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        answer = resp["choices"][0]["message"]["content"]
        msg = await update.message.reply_text(f"🤖 GPT:\n{answer}\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ GPT lỗi: {e}")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))


# GROK (xAI)
async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not XAI_API_KEY:
        msg = await update.message.reply_text("❌ GROK lỗi: Chưa có API_KEY")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
        return
    try:
        question = " ".join(context.args) if context.args else "Hello"
        url = "https://api.x.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
        data = {
            "model": "grok-2",
            "messages": [{"role": "user", "content": question}]
        }
        resp = requests.post(url, headers=headers, json=data).json()
        answer = resp["choices"][0]["message"]["content"]
        msg = await update.message.reply_text(f"🧠 GROK:\n{answer}\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ GROK lỗi: {e}")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))


# GEMINI
async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not GEMINI_API_KEY:
        msg = await update.message.reply_text("❌ GEMINI lỗi: Chưa có API_KEY")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
        return
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        question = " ".join(context.args) if context.args else "Hello"
        resp = model.generate_content(question)
        answer = resp.text
        msg = await update.message.reply_text(f"🌌 GEMINI:\n{answer}\n\n⏳ Tin nhắn sẽ tự xoá sau 5 phút.")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ GEMINI lỗi: {e}")
        context.application.create_task(delete_after_delay(context, update.effective_chat.id, [msg.message_id]))
