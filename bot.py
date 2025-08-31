import asyncio
import os
import requests
from datetime import datetime, timedelta
from telegram import Update, ChatPermissions, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# ====== TOKEN ======
TOKEN = os.environ.get("TOKEN")

# ====== AUTO DELETE ======
async def auto_delete(msg, delay: int):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except:
        pass

async def delete_user_message(update: Update):
    try:
        await update.message.delete()
    except:
        pass

# ====== CHECK ADMIN ======
def is_admin(update: Update) -> bool:
    user_id = update.message.from_user.id
    chat_admins = update.effective_chat.get_administrators()
    return any(admin.user.id == user_id for admin in chat_admins)

# ====== /start ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    msg = await update.message.reply_text("👋 Xin chào! Gõ /help để xem lệnh.")
    asyncio.create_task(auto_delete(msg, 30))

# ====== /help ======
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 Các lệnh hiện có:\n\n"
        "📌 Người dùng:\n"
        "/start - Bắt đầu\n"
        "/help - Hướng dẫn\n"
        "/id - Lấy ID của bạn\n"
        "/time - Xem giờ thế giới\n"
        "/ip <địa chỉ> - Tra cứu IP\n"
        "/short <link> - Rút gọn link\n"
        "/proxy - Lấy proxy ngẫu nhiên\n"
        "/tiktok <link> - Tải video TikTok\n"
        "/tiktokinfo <link> - Lấy info video TikTok\n\n"
        "🛠️ Admin:\n"
        "/shutdown - Tắt bot\n"
        "/restart - Khởi động lại bot\n"
        "/startbot - Chạy lại bot\n"
        "/mute <time> (reply user) - Khoá mõm (vd: 1p, 10p, 1m, 1b)\n"
        "/unmute (reply user) - Mở mõm\n"
        "/ban (reply user) - Ban vĩnh viễn\n"
        "/kick (reply user) - Đá khỏi nhóm (có thể vào lại)\n"
    )
    msg = await update.message.reply_text(help_text)
    asyncio.create_task(auto_delete(msg, 60))

# ====== ADMIN COMMANDS ======
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền")
        asyncio.create_task(auto_delete(msg, 30))
        return
    msg = await update.message.reply_text("🛑 Bot đã tắt")
    asyncio.create_task(auto_delete(msg, 30))
    os._exit(0)

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền")
        asyncio.create_task(auto_delete(msg, 30))
        return
    msg = await update.message.reply_text("🔄 Bot đang khởi động lại...")
    asyncio.create_task(auto_delete(msg, 30))
    os.execl(sys.executable, sys.executable, *os.sys.argv)

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền")
        asyncio.create_task(auto_delete(msg, 30))
        return
    msg = await update.message.reply_text("🚀 Bot đã khởi động lại")
    asyncio.create_task(auto_delete(msg, 30))

# ====== /mute ======
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này")
        asyncio.create_task(auto_delete(msg, 30))
        return

    if not update.message.reply_to_message or not context.args:
        msg = await update.message.reply_text("⚠️ Dùng: reply user + /mute <time> (vd: 1p, 10p, 1m, 1b)")
        asyncio.create_task(auto_delete(msg, 30))
        return

    time_str = context.args[0]
    unit = time_str[-1]
    try:
        value = int(time_str[:-1])
    except:
        msg = await update.message.reply_text("⚠️ Sai định dạng thời gian (vd: 10p, 1m, 1b)")
        asyncio.create_task(auto_delete(msg, 30))
        return

    seconds = 0
    if unit == "p": seconds = value * 60
    elif unit == "m": seconds = value * 3600
    elif unit == "b": seconds = value * 86400
    else:
        msg = await update.message.reply_text("⚠️ Đơn vị phải là p (phút), m (giờ), b (ngày)")
        asyncio.create_task(auto_delete(msg, 30))
        return

    until = datetime.utcnow() + timedelta(seconds=seconds)
    user_id = update.message.reply_to_message.from_user.id

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=until
        )
        msg = await update.message.reply_text(
            f"🔇 Đã khoá mõm {update.message.reply_to_message.from_user.mention_html()} trong {time_str}",
            parse_mode="HTML"
        )
        asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ Lỗi khi mute: {e}")
        asyncio.create_task(auto_delete(msg, 30))

# ====== /unmute ======
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền dùng lệnh này")
        asyncio.create_task(auto_delete(msg, 30))
        return

    if not update.message.reply_to_message:
        msg = await update.message.reply_text("⚠️ Dùng: reply user + /unmute")
        asyncio.create_task(auto_delete(msg, 30))
        return

    user_id = update.message.reply_to_message.from_user.id

    try:
        await context.bot.restrict_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            permissions=ChatMember.DEFAULT,
            until_date=None
        )
        msg = await update.message.reply_text(
            f"🔓 Đã unmute {update.message.reply_to_message.from_user.mention_html()}",
            parse_mode="HTML"
        )
        asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ Lỗi khi unmute: {e}")
        asyncio.create_task(auto_delete(msg, 30))

# ====== /ban ======
async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền")
        asyncio.create_task(auto_delete(msg, 30))
        return

    if not update.message.reply_to_message:
        msg = await update.message.reply_text("⚠️ Dùng: reply user + /ban")
        asyncio.create_task(auto_delete(msg, 30))
        return

    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        msg = await update.message.reply_text(
            f"🚫 Đã ban {update.message.reply_to_message.from_user.mention_html()}",
            parse_mode="HTML"
        )
        asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ Lỗi khi ban: {e}")
        asyncio.create_task(auto_delete(msg, 30))

# ====== /kick ======
async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)
    if not is_admin(update):
        msg = await update.message.reply_text("⛔ Bạn không có quyền")
        asyncio.create_task(auto_delete(msg, 30))
        return

    if not update.message.reply_to_message:
        msg = await update.message.reply_text("⚠️ Dùng: reply user + /kick")
        asyncio.create_task(auto_delete(msg, 30))
        return

    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(
            chat_id=update.effective_chat.id,
            user_id=user_id,
            until_date=datetime.utcnow() + timedelta(seconds=60)
        )
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)

        msg = await update.message.reply_text(
            f"👢 Đã kick {update.message.reply_to_message.from_user.mention_html()}",
            parse_mode="HTML"
        )
        asyncio.create_task(auto_delete(msg, 30))
    except Exception as e:
        msg = await update.message.reply_text(f"⚠️ Lỗi khi kick: {e}")
        asyncio.create_task(auto_delete(msg, 30))

# ====== MAIN ======
def main():
    app = Application.builder().token(TOKEN).build()

    # user
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    # (các lệnh khác của bạn như /time, /ip, /short, /proxy, /tiktok, /tiktokinfo vẫn giữ nguyên ở đây)

    # admin
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CommandHandler("startbot", startbot))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("kick", kick))

    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()