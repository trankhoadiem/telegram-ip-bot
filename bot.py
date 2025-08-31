import os
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Fake device info
FAKE_SERIAL = "H7YQ9ABCDN12"
FAKE_IMEI = "356789123456789"

# /start – fake connect
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Vui lòng kết nối thiết bị với máy chủ (Server To Minh Diem V1.300.000)...")
    await asyncio.sleep(5)
    await update.message.reply_text(
        f"✅ Thiết bị đã kết nối!\n\n*Model:* iPhone 14 Plus\n*Serial:* {FAKE_SERIAL}\n*IMEI:* {FAKE_IMEI}",
        parse_mode=ParseMode.MARKDOWN
    )

# /help – fake command list
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔧 Available commands:\n\n"
        "/bypass – not active\n"
        "/bypasshello – Start simulated bypass process\n"
        "/Passwork – not active\n"
        "/CheckPHONE – not active\n"
    )
    await update.message.reply_text(text)

# /bypasshello – fake bypass with progress
async def bypasshello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚀 Starting bypass process... (Simulation)\n")

    steps = [
        "Loading exploit modules...",
        "Connecting to device...",
        "Checking RAMRick exploit...",
        "Patching Secure Enclave...",
        "Uploading payload...",
        "Running unlocktool scripts...",
        "Bypassing iCloud lock...",
        "Finalizing unlock..."
    ]

    for i, step in enumerate(steps):
        percent = int(((i + 1) / len(steps)) * 100)
        bar = "▓" * (percent // 10) + "░" * (10 - (percent // 10))
        await update.message.reply_text(f"{bar} {percent}% — {step}")
        await asyncio.sleep(3)  # 3s mỗi bước ~ 24s tổng

    await update.message.reply_text("✅ Done — Device Unlocked")

def main():
    if not TOKEN:
        raise RuntimeError("Missing TELEGRAM_TOKEN in environment")

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("bypasshello", bypasshello))

    print("Bot is running…")
    app.run_polling()

if __name__ == "__main__":
    main()
