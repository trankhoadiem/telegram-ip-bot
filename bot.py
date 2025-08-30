from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import sys
import openai
import google.generativeai as genai

# ==== TOKEN & API KEYS ====
TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
XAI_API_KEY = os.environ.get("XAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")   # Gemini key

# ==== ADMIN ====
ADMIN_USERNAME = "DuRinn_LeTuanDiem"

def is_admin(update: Update):
    user = update.effective_user
    return user and user.username == ADMIN_USERNAME

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# =======================
# 🚀 Helper - xóa tin nhắn người dùng (an toàn)
# =======================
async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except Exception:
        pass

# =======================
# 🚀 AI MODE
# =======================
async def ai_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = None
    await update.message.reply_text(
        "🤖 Đã bật **Chế độ AI**\n\n"
        "👉 Chọn model để trò chuyện:\n"
        "🧠 /gpt - ChatGPT\n"
        "🦉 /grok - Grok\n"
        "🌌 /gemini - Gemini\n"
        "❌ /exit - Thoát chế độ AI"
    )

async def exit_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = None
    await update.message.reply_text("✅ Bạn đã thoát khỏi **Chế độ AI**.")

# chọn model
async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = "gpt"
    await update.message.reply_text("🧠 Bạn đang trò chuyện với **ChatGPT**. Hãy nhập tin nhắn... (/exit để thoát)")

async def grok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = "grok"
    await update.message.reply_text("🦉 Bạn đang trò chuyện với **Grok**. Hãy nhập tin nhắn... (/exit để thoát)")

async def gemini(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    context.user_data["ai_mode"] = "gemini"
    await update.message.reply_text("🌌 Bạn đang trò chuyện với **Gemini**. Hãy nhập tin nhắn... (/exit để thoát)")

# xử lý tin nhắn khi đang trong chế độ AI
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get("ai_mode")
    if not mode:
        return

    query = update.message.text.strip()

    thinking_msg = await update.message.reply_text("⏳ Đang suy nghĩ...")
    try:
        # xóa tin nhắn người dùng để giữ chat gọn
        try:
            await update.message.delete()
        except:
            pass

        if mode == "gpt":
            if not OPENAI_API_KEY:
                reply = "⚠️ OPENAI_API_KEY chưa cấu hình."
            else:
                openai.api_key = OPENAI_API_KEY
                res = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": query}]
                )
                reply = res.choices[0].message["content"]

        elif mode == "grok":
            if not XAI_API_KEY:
                reply = "⚠️ XAI_API_KEY chưa cấu hình."
            else:
                headers = {"Authorization": f"Bearer {XAI_API_KEY}"}
                resp = requests.post(
                    "https://api.x.ai/v1/chat/completions",
                    headers=headers,
                    json={"model": "grok-4-0709", "messages": [{"role": "user", "content": query}]}
                )
                data = resp.json()
                reply = data.get("choices", [{}])[0].get("message", {}).get("content", "⚠️ Lỗi khi gọi Grok.")

        elif mode == "gemini":
            if not GOOGLE_API_KEY:
                reply = "⚠️ GOOGLE_API_KEY chưa cấu hình."
            else:
                genai.configure(api_key=GOOGLE_API_KEY)
                model = genai.GenerativeModel("gemini-1.5-flash")
                resp = model.generate_content(query)
                reply = getattr(resp, "text", "⚠️ Lỗi khi gọi Gemini.")

        else:
            reply = "⚠️ Chưa chọn model AI."
    except Exception as e:
        reply = f"⚠️ Lỗi {mode.upper()}: {e}"

    await thinking_msg.edit_text(reply)

# =======================
# 🚀 Admin Commands
# =======================
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("🛑 Bot đang **tắt**...")
    await context.application.stop()

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("♻️ Bot đang **khởi động lại**...")
    os.execv(sys.executable, ["python"] + sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này.")
        return
    await update.message.reply_text("✅ Bot đang chạy bình thường!")

# =======================
# 🚀 Các lệnh khác
# =======================

async def start(update, context):
    # giữ nguyên phần giới thiệu như bạn yêu cầu
    await update.message.reply_text(
        "✨ **Chào mừng bạn đến với BOT** ✨\n\n"
        "🤖 Công cụ: 🌐 Kiểm tra IP | 🎬 Tải TikTok | 🤖 Chat AI (GPT, Grok, Gemini)\n\n"
        "⚡ Bot vẫn đang **cập nhật hằng ngày**, có thể tồn tại một số lỗi.\n\n"
        "📌 Thành viên phát triển BOT:\n"
        "   👤 Tô Minh Điềm – Telegram: @DuRinn_LeTuanDiem\n"
        "   👤 Telegram Support – @Telegram\n"
        "   🤖 Bot chính thức – @ToMinhDiem_bot\n\n"
        "💡 Gõ /help để xem tất cả lệnh khả dụng."
    )

async def help_command(update, context):
    # hướng dẫn chi tiết, dài theo yêu cầu
    text = (
        "📖 *Hướng dẫn sử dụng BOT* (chi tiết)\n\n"
        "🔹 *Khởi động & Giới thiệu*\n"
        "  /start — Hiển thị thông tin giới thiệu.\n"
        "  /help — Hiển thị hướng dẫn chi tiết này.\n\n"
        "🔹 *Chế độ AI* (trò chuyện thông minh)\n"
        "  /ai — Bật chế độ AI. Sau đó chọn model để trò chuyện:\n"
        "    • /gpt — Chuyển sang ChatGPT (dùng OPENAI_API_KEY).\n"
        "    • /grok — Chuyển sang Grok (dùng XAI_API_KEY).\n"
        "    • /gemini — Chuyển sang Gemini (dùng GOOGLE_API_KEY).\n"
        "    • /exit — Thoát chế độ AI.\n"
        "  *Cách dùng*: bật /ai → chọn model → gửi tin nhắn → bot trả lời. Tin nhắn người dùng sẽ được xóa để giữ chat gọn.\n\n"
        "🔹 *Kiểm tra IP*\n"
        "  /ip <địa-chỉ-ip> — Ví dụ: `/ip 8.8.8.8`\n"
        "  Bot trả về: quốc gia, thành phố, múi giờ, ISP, tọa độ.\n\n"
        "🔹 *Tải TikTok*\n"
        "  /tiktok <link> — Ví dụ: `/tiktok https://www.tiktok.com/@user/video/123`\n"
        "  - Bot sẽ cố gắng tải video chất lượng cao (HD nếu có), hoặc gửi ảnh nếu link là album.\n"
        "  - Nếu link sai hoặc dịch vụ không hỗ trợ, bot sẽ báo lỗi.\n\n"
        "🔹 *Thông tin TikTok*\n"
        "  /tiktokinfo <username> — Ví dụ: `/tiktokinfo vietnamese_user` hoặc `/tiktokinfo @user`\n"
        "  - Bot sẽ lấy avatar, tên, sec-uid, follower, following, total likes, số video, bio, quốc gia, verified, ngày tạo (nếu có).\n"
        "  - Lưu ý: dữ liệu phụ thuộc vào nguồn (Tikwm). Nếu thiếu thông tin, bot sẽ hiển thị 'Không rõ' hoặc 'Không công khai'.\n\n"
        "🔹 *Lệnh Admin*\n"
        "  (Chỉ admin @DuRinn_LeTuanDiem mới dùng được)\n"
        "  /shutdown — Tắt bot.\n"
        "  /restart — Khởi động lại bot.\n"
        "  /startbot — Kiểm tra trạng thái bot.\n\n"
        "🔹 *Ghi chú vận hành & môi trường*\n"
        "  • Đặt biến môi trường trong Railway/Heroku/Server: TOKEN, OPENAI_API_KEY (nếu dùng GPT), XAI_API_KEY (Grok), GOOGLE_API_KEY (Gemini).\n"
        "  • Nếu gặp lỗi liên quan API key: kiểm tra xem biến môi trường đã cấu hình đúng chưa.\n"
        "  • TikTok API (tikwm) có lúc không trả đủ data — đây là giới hạn bên thứ 3.\n"
        "  • Bot xóa tin nhắn lệnh để giữ chat gọn: nếu bạn muốn giữ bản sao lệnh thì gửi dưới dạng reply hoặc dùng private chat.\n\n"
        "📌 *Ví dụ nhanh*:\n"
        "  1) /ip 1.1.1.1\n"
        "  2) /tiktok https://www.tiktok.com/@nhan/video/123456\n"
        "  3) /tiktokinfo @nhan\n"
        "  4) /ai -> /gpt -> Gõ: 'Viết cho tôi 1 bài giới thiệu ngắn về bot'\n\n"
        "Nếu cần mình hướng dẫn deploy lên Railway hoặc lấy API keys, gõ: `@DuRinn_LeTuanDiem` hoặc hỏi trực tiếp.\n"
    )
    await update.message.reply_text(text)

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
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text("👉 Dùng: /ip 8.8.8.8")
        return
    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url:
        await update.message.reply_photo(flag_url, caption=info)
    else:
        await update.message.reply_text(info)

async def download_tiktok(update, context):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>")
        return
    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok...")
    try:
        res = requests.post(TIKWM_API, data={"url": link}, headers=HEADERS, timeout=20)
        data_json = res.json()
        if data_json.get("code") != 0 or "data" not in data_json:
            await waiting_msg.edit_text("❌ Không tải được TikTok. Vui lòng kiểm tra lại link!")
            return
        data = data_json["data"]
        title = data.get("title", "TikTok")
        if data.get("hdplay") or data.get("play"):
            url = data.get("hdplay") or data.get("play")
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f"🎬 {title} (HQ)")
        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)
        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== TikTok info (nhiều trường, fallback khi thiếu)
async def tiktok_info(update, context):
    await delete_user_message(update)
    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktokinfo <username>")
        return
    username = context.args[0].strip().replace("@", "")
    waiting_msg = await update.message.reply_text(f"⏳ Đang lấy thông tin TikTok @{username}...")
    try:
        api_url = f"https://www.tikwm.com/api/user/info?unique_id={username}"
        resp = requests.get(api_url, headers=HEADERS, timeout=15)
        # Một số lúc tikwm trả text/html hoặc khác -> cố gắng parse json
        try:
            res = resp.json()
        except Exception:
            res = {}

        user = res.get("data", {}) if isinstance(res, dict) else {}

        avatar = user.get("avatar", "")
        nickname = user.get("nickname", "N/A")
        uid = user.get("unique_id", username)
        secid = user.get("sec_uid", "Không có")
        followers = user.get("follower_count", "Ẩn")
        following = user.get("following_count", "Ẩn")
        heart = user.get("total_favorited", "Ẩn")
        video_count = user.get("aweme_count", "Ẩn")
        bio = user.get("signature", "Không có")
        region = user.get("region", "Không rõ")
        verified = "✅ Có" if user.get("verified") else "❌ Không"
        # một số API trả create_time (timestamp) hoặc str
        create_time = user.get("create_time", user.get("create_time_str", "Không rõ"))
        birthday = user.get("birthday", "Không công khai")

        caption = (
            f"📱 Thông tin TikTok @{uid}:\n"
            f"👤 Tên hiển thị: {nickname}\n"
            f"🆔 Sec-UID: {secid}\n"
            f"🌍 Quốc gia / Region: {region}\n"
            f"✔️ Verified: {verified}\n"
            f"🎂 Ngày sinh: {birthday}\n"
            f"📅 Ngày tạo (nếu có): {create_time}\n"
            f"👥 Followers: {followers}\n"
            f"👤 Following: {following}\n"
            f"❤️ Tổng like: {heart}\n"
            f"🎬 Số video: {video_count}\n"
            f"📝 Bio: {bio}"
        )

        if avatar:
            try:
                await waiting_msg.delete()
            except:
                pass
            await update.message.reply_photo(avatar, caption=caption)
        else:
            await waiting_msg.edit_text(caption)
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi lấy TikTok info: {e}")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🎉👋 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!"
        )

# =======================
# 🚀 MAIN
# =======================
def main():
    app = Application.builder().token(TOKEN).build()

    # AI
    app.add_handler(CommandHandler("ai", ai_mode))
    app.add_handler(CommandHandler("exit", exit_ai))
    app.add_handler(CommandHandler("gpt", gpt))
    app.add_handler(CommandHandler("grok", grok))
    app.add_handler(CommandHandler("gemini", gemini))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_ai_message))

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

    # Welcome
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
