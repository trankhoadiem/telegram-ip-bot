from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import os

TOKEN = os.environ.get("TOKEN")

# ========== HÀM GỬI TIN NHẮN CÓ AUTO XÓA ==========
async def send_temp_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, delay: int = 60, reply_markup=None):
    msg = await update.message.reply_text(
        text + f"\n\n🕒 (Tin nhắn này sẽ tự động xoá sau {delay} giây)",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

# ========== /start ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📖 Hướng dẫn", callback_data="help")],
        [InlineKeyboardButton("🌐 Tra IP", callback_data="ip")],
        [InlineKeyboardButton("🎬 Tải TikTok", callback_data="tiktok")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "✨ *Chào mừng bạn đến với BOT* ✨\n\n"
        "🤖 Công cụ chính:\n"
        "  • 🌐 Kiểm tra thông tin IP\n"
        "  • 🎬 Tải video/ảnh từ TikTok\n"
        "  • 📱 Lấy thông tin tài khoản TikTok\n"
        "  • 🔧 AI (hiện đang bảo trì)\n\n"
        "📌 *Nhà phát triển*: Tô Minh Điềm – @DuRinn_LeTuanDiem"
    )

    await send_temp_message(update, context, text, 60, reply_markup)

# ========== /help ==========
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📖 *HƯỚNG DẪN CHI TIẾT A–Z* 📖\n\n"
        "1) /start  \n"
        "   ➝ Bắt đầu và hiển thị thông tin giới thiệu bot.  \n"
        "   ➝ Có các nút bấm để truy cập nhanh lệnh chính.  \n\n"
        "2) /help  \n"
        "   ➝ Danh sách toàn bộ lệnh, mô tả chi tiết.  \n\n"
        "3) /ip <địa_chỉ_ip>  \n"
        "   ➝ Tra cứu thông tin IP (Vị trí, Nhà mạng, Quốc gia...).  \n"
        "   Ví dụ: `/ip 8.8.8.8`  \n\n"
        "4) /tiktok <link>  \n"
        "   ➝ Tải video hoặc ảnh TikTok chất lượng cao, không logo.  \n"
        "   ➝ Hỗ trợ cả video dài & slide ảnh.  \n"
        "   Ví dụ: `/tiktok https://vt.tiktok.com/xxxx/`  \n\n"
        "5) /tiktokinfo <username>  \n"
        "   ➝ Lấy thông tin chi tiết tài khoản TikTok:  \n"
        "      • Tên hiển thị  \n"
        "      • Username  \n"
        "      • Ảnh đại diện  \n"
        "      • Số người theo dõi, tim, video...  \n"
        "   Ví dụ: `/tiktokinfo username`  \n\n"
        "6) /ai <câu_hỏi>  \n"
        "   ➝ Chat với AI (hiện đang bảo trì).  \n\n"
        "7) /shutdown  \n"
        "   ➝ Tắt bot (chỉ Admin).  \n\n"
        "8) /restart  \n"
        "   ➝ Khởi động lại bot (chỉ Admin).  \n\n"
        "9) /startbot  \n"
        "   ➝ Khởi động bot sau khi tắt (chỉ Admin).  \n\n"
        "─────────────────────────────\n"
        "📌 *Nhà phát triển*: Tô Minh Điềm – @DuRinn_LeTuanDiem"
    )

    await send_temp_message(update, context, text, 60)

# ========== MAIN ==========
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    print("🤖 Bot đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()