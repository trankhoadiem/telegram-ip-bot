from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import requests
import soundcloud
import os

# ==== TOKEN ====
TOKEN = os.environ.get(TOKEN)  # Thêm TOKEN bot của bạn từ BotFather

# ==== TikTok API ====
TIKWM_API = httpswww.tikwm.comapi
HEADERS = {
    User-Agent Mozilla5.0,
    Referer httpswww.tikwm.com
}

# ==== start ====
async def start(update, context)
    await update.message.reply_text(
        ✨ Chào mừng bạn đến với BOT ✨nn
        🤖 Công cụ tra cứu IP & tải TikTok videoảnh, YouTube Shorts, SoundCloud.nn
        📌 Các thành viên phát triển BOTn
           👤 Tô Minh Điềm – Telegram @DuRinn_LeTuanDiemn
           👤 Telegram Support – @Telegramn
           🤖 Bot chính thức – @ToMinhDiem_botnn
        💡 Gõ help để xem lệnh khả dụng.
    )

# ==== help ====
async def help_command(update, context)
    await update.message.reply_text(
        📖 Lệnh có sẵnnn
        start - Bắt đầun
        help - Trợ giúpn
        ip địa chỉ ip - Kiểm tra thông tin IPn
        tiktok link - Tải videoảnh TikTokn
        yt link - Tải video YouTube Shortsn
        sc link - Tải âm thanh SoundCloudn
    )

# ==== Check IP ====
def get_ip_info(ip)
    try
        url = fhttpip-api.comjson{ip}fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query
        res = requests.get(url, timeout=15).json()

        if res.get(status) == fail
            return None, f❌ Không tìm thấy thông tin cho IP {ip}

        info = (
            f🌍 Thông tin IP {res['query']}n
            f🗺 Quốc gia {res['country']} ({res['countryCode']})n
            f🏙 Khu vực {res['regionName']} - {res['city']} ({res.get('zip','')})n
            f🕒 Múi giờ {res['timezone']}n
            f📍 Toạ độ {res['lat']}, {res['lon']}n
            f📡 ISP {res['isp']}n
            f🏢 Tổ chức {res['org']}n
            f🔗 AS {res['as']}
        )
        flag_url = fhttpsflagcdn.comw320{res['countryCode'].lower()}.png
        return flag_url, info
    except Exception as e
        return None, f⚠️ Lỗi khi kiểm tra IP {e}

async def check_ip(update, context)
    try
        await update.message.delete()
    except
        pass

    if not context.args
        await update.message.reply_text(👉 Dùng ip 8.8.8.8)
        return

    ip = context.args[0].strip()
    flag_url, info = get_ip_info(ip)
    if flag_url
        await update.message.reply_photo(flag_url, caption=info)
    else
        await update.message.reply_text(info)

# ==== TikTok Downloader ====
async def download_tiktok(update, context)
    try
        await update.message.delete()
    except
        pass

    if not context.args
        await update.message.reply_text(👉 Dùng tiktok link TikTok)
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text(⏳ Đang xử lý link TikTok, vui lòng chờ...)

    try
        res = requests.post(TIKWM_API, data={url link}, headers=HEADERS, timeout=20)
        data_json = res.json()

        if data_json.get(code) != 0 or data not in data_json
            await waiting_msg.edit_text(❌ Không tải được TikTok. Vui lòng kiểm tra lại link!)
            return

        data = data_json[data]
        title = data.get(title, TikTok)

        # Nếu là video
        if data.get(hdplay) or data.get(play)
            url = data.get(hdplay) or data.get(play)
            await waiting_msg.delete()
            await update.message.reply_video(url, caption=f🎬 {title} (chất lượng cao nhất))

        # Nếu là bài ảnh
        elif data.get(images)
            await waiting_msg.edit_text(f🖼 {title}nnĐang gửi ảnh gốc...)
            for img_url in data[images]
                await update.message.reply_photo(img_url)

        else
            await waiting_msg.edit_text(⚠️ Không tìm thấy videoảnh trong link này.)

    except Exception as e
        await waiting_msg.edit_text(f⚠️ Lỗi khi tải TikTok {e})

# ==== YouTube Downloader (Shorts) ====
async def download_youtube(update, context)
    if not context.args
        await update.message.reply_text(👉 Dùng yt link YouTube)
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text(⏳ Đang xử lý link YouTube, vui lòng chờ...)

    try
        ydl_opts = {
            'format' 'bestaudiobest',  # Chọn chất lượng tốt nhất
            'outtmpl' 'downloads%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl
            info_dict = ydl.extract_info(link, download=True)
            video_url = info_dict.get('url', None)

            await waiting_msg.delete()
            await update.message.reply_video(video_url, caption=f🎬 YouTube Short {info_dict.get('title', 'Video')})
    except Exception as e
        await waiting_msg.edit_text(f⚠️ Lỗi khi tải video YouTube {e})

# ==== SoundCloud Downloader ====
async def download_soundcloud(update, context)
    if not context.args
        await update.message.reply_text(👉 Dùng sc link SoundCloud)
        return

    link = context.args[0].strip()
    waiting_msg = await update.message.reply_text(⏳ Đang xử lý link SoundCloud, vui lòng chờ...)

    try
        scdl_url = fhttpsscdl.com{link}
        await waiting_msg.delete()
        await update.message.reply_text(fTải nhạc từ SoundCloud tại {scdl_url})
    except Exception as e
        await waiting_msg.edit_text(f⚠️ Lỗi khi tải từ SoundCloud {e})

# ==== Main ====
def main()
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler(start, start))
    app.add_handler(CommandHandler(help, help_command))
    app.add_handler(CommandHandler(ip, check_ip))
    app.add_handler(CommandHandler(tiktok, download_tiktok))
    app.add_handler(CommandHandler(yt, download_youtube))
    app.add_handler(CommandHandler(sc, download_soundcloud))

    # Run the bot
    app.run_polling()

if __name__ == __main__
    main()
