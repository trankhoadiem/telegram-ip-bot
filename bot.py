from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os

# ==== TOKEN ====
TOKEN = os.environ.get("TOKEN")

# ==== TikTok API ====
TIKWM_API = "https://www.tikwm.com/api/"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.tikwm.com/"
}

# ==== SoundCloud API ====
SOUNDCLOUD_API = "https://api.soundcloud.com/tracks"
SOUNDCLOUD_CLIENT_ID = "YOUR_SOUNDCLOUD_CLIENT_ID"  # Cần có CLIENT_ID từ SoundCloud

# ==== /start ====
async def start(update, context):
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

# ==== /help ====
async def help_command(update, context):
    await update.message.reply_text(
        "📖 **Hướng dẫn sử dụng BOT chi tiết** 📖\n\n"
        "✨ Bot hỗ trợ nhiều tính năng tiện ích và AI thông minh:\n\n"
        "🔹 /start - Giới thiệu bot và thông tin cơ bản.\n"
        "🔹 /help - Hiển thị danh sách lệnh kèm mô tả chi tiết.\n\n"
        "🤖 **Chế độ AI**:\n"
        "   • /ai - Bật chế độ AI và chọn model để trò chuyện (hiện tại đang bảo trì).\n"
        "   • /gpt - Dùng ChatGPT để hỏi đáp, hỗ trợ thông minh (hiện tại đang bảo trì).\n"
        "   • /grok - Dùng Grok (xAI), phong cách khác biệt hơn (hiện tại đang bảo trì).\n"
        "   • /gemini - Dùng Gemini (Google), phản hồi nhanh và súc tích (hiện tại đang bảo trì).\n"
        "   • /exit - Thoát khỏi chế độ AI.\n\n"
        "🌐 **Công cụ khác**:\n"
        "   • /ip <ip> - Kiểm tra thông tin chi tiết của một địa chỉ IP.\n"
        "   • /tiktok <link> - Tải video/ảnh TikTok không watermark.\n"
        "   • /testapi - Kiểm tra trạng thái các API key (GPT, Grok, Gemini).\n\n"
        "🔒 **Lệnh Admin**:\n"
        "   • /shutdown - Tắt bot.\n"
        "   • /restart - Khởi động lại bot.\n"
        "   • /startbot - Kiểm tra bot đang chạy.\n\n"
        "💡 Lưu ý: Một số lệnh yêu cầu bạn phải nhập đúng cú pháp để bot hiểu.\n"
        "👉 Hãy thử ngay bằng cách gõ /ai và chọn mô hình AI yêu thích!"
    )

# ==== Tải video TikTok ====
async def download_tiktok(update, context):
    try:
        await update.message.delete()
    except:
        pass

    if not context.args:
        await update.message.reply_text("👉 Dùng: /tiktok <link TikTok>")
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text("⏳ Đang xử lý link TikTok, vui lòng chờ...")

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
            await update.message.reply_video(url, caption=f"🎬 {title} (chất lượng cao nhất)")

        elif data.get("images"):
            await waiting_msg.edit_text(f"🖼 {title}\n\nĐang gửi ảnh gốc...")
            for img_url in data["images"]:
                await update.message.reply_photo(img_url)

        else:
            await waiting_msg.edit_text("⚠️ Không tìm thấy video/ảnh trong link này.")
    except Exception as e:
        await waiting_msg.edit_text(f"⚠️ Lỗi khi tải TikTok: {e}")

# ==== Tìm nhạc từ SoundCloud ====
async def search_soundcloud(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /soundcloud <tên bài hát>")
        return

    query = " ".join(context.args)
    url = f"{SOUNDCLOUD_API}?client_id={SOUNDCLOUD_CLIENT_ID}&q={query}"

    try:
        res = requests.get(url).json()

        if not res:
            await update.message.reply_text("❌ Không tìm thấy bài hát nào trên SoundCloud.")
            return

        track = res[0]
        track_title = track["title"]
        track_url = track["permalink_url"]
        track_stream_url = track["stream_url"] + "?client_id=" + SOUNDCLOUD_CLIENT_ID

        await update.message.reply_text(f"🎵 Bài hát: {track_title}\nLink SoundCloud: {track_url}\nTải nhạc tại: {track_stream_url}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi tìm nhạc: {e}")

# ==== Tìm ảnh từ SoundCloud ====
async def search_image_from_soundcloud(update, context):
    if not context.args:
        await update.message.reply_text("👉 Dùng: /image <tên bài hát>")
        return

    query = " ".join(context.args)
    url = f"{SOUNDCLOUD_API}?client_id={SOUNDCLOUD_CLIENT_ID}&q={query}"

    try:
        res = requests.get(url).json()

        if not res:
            await update.message.reply_text("❌ Không tìm thấy ảnh nào từ SoundCloud.")
            return

        track = res[0]
        artwork_url = track.get("artwork_url")
        if artwork_url:
            artwork_url = artwork_url.replace("large", "t300x300")  # Thay đổi kích thước ảnh
            await update.message.reply_photo(artwork_url)
        else:
            await update.message.reply_text("⚠️ Không tìm thấy ảnh cho bài hát này.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Lỗi khi tìm ảnh: {e}")

# ==== Welcome New Member ====
async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"🎉 Chào mừng {member.full_name} đã tham gia nhóm {update.message.chat.title}!"
        )

# ==== Main ==== 
def main():
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ip", check_ip))
    app.add_handler(CommandHandler("tiktok", download_tiktok))
    app.add_handler(CommandHandler("soundcloud", search_soundcloud))
    app.add_handler(CommandHandler("image", search_image_from_soundcloud))

    # Welcome new members
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
