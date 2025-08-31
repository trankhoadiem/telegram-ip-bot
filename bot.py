import os
import textwrap
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Fake device info for prank
FAKE_SERIAL = "H7YQ9ABCDN12"
FAKE_IMEI = "356789123456789"

# /start – simulate connect to server then show fake device info
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Vui lòng kết nối thiết bị với máy chủ (Server To Minh Diem V12)...")
    await asyncio.sleep(10)
    await update.message.reply_text(
        f"✅ Thiết bị đã kết nối!\n\n*Model:* iPhone 14 Plus\n*Serial:* {FAKE_SERIAL}\n*IMEI:* {FAKE_IMEI}",
        parse_mode=ParseMode.MARKDOWN
    )

# /help – show fake command list
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = textwrap.dedent(
        """
        🔧 Available commands:

        /bypass – (Demo, not active)
        /bypasshello – Start simulated bypass process
        /Passwork – (Demo, not active)
        /CheckPHONE – (Demo, not active)
        """
    ).strip()
    await update.message.reply_text(text)

# /bypasshello – run fake bypass process with progress %
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

    total_time = 30  # ~30 seconds simulation
    step_interval = total_time // len(steps)

    progress = 0
    for i, step in enumerate(steps):
        await update.message.reply_text(f"[{progress}%] {step}")
        await asyncio.sleep(step_interval)
        progress = int(((i+1) / len(steps)) * 100)

    # Finish with 100%
    await update.message.reply_text(f"[100%] ✅ Done — Device Unlocked (Simulation)")

async def main():
    if not TOKEN:
        raise RuntimeError("Missing TELEGRAM_TOKEN in environment")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("bypasshello", bypasshello))

    print("Bot is running… Press Ctrl+C to stop.")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
