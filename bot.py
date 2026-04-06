import os
import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.bot import DefaultBotProperties
from aiohttp import web
import yt_dlp
import io

# =============================
# Token va port sozlamalari
# =============================
TOKEN = os.getenv("BOT_API")
PORT = int(os.getenv("PORT", 8000))

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher()

# =============================
# /start komandasi
# =============================
@dp.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("Salom! Video yoki rasm linkini yuboring.")

# =============================
# Video / rasm linklarni yuklash
# =============================
@dp.message(F.text)
async def download_media(message: types.Message):
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.answer("Iltimos, to‘g‘ri URL yuboring.")
        return

    await message.answer("Yuklanmoqda, biroz kuting...")

    buffer = io.BytesIO()

    ydl_opts = {
        'format': 'best',
        'outtmpl': '-',  # faylni diskga saqlamaymiz
        'noplaylist': True,
        'quiet': True,
        'progress_hooks': [],
        'logger': None
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url_to_download = info.get("url")  # media url
            # Telegram-ga yuborish
            if info.get("ext") in ['mp4', 'mkv', 'webm']:
                await bot.send_video(message.chat.id, url_to_download)
            elif info.get("ext") in ['jpg', 'png', 'webp']:
                await bot.send_photo(message.chat.id, url_to_download)
            else:
                await message.answer("Media turi qo‘llab-quvvatlanmaydi.")
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {e}")

# =============================
# Web server va webhook
# =============================
async def handle(request):
    update = types.Update(**await request.json())
    await dp.update_router.feed_update(update)
    return web.Response(text="OK")

async def on_startup(app):
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    await bot.set_webhook(webhook_url)

async def on_cleanup(app):
    await bot.delete_webhook()
    await bot.session.close()

app = web.Application()
app.router.add_post("/webhook", handle)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

# =============================
# Botni ishga tushurish
# =============================
if __name__ == "__main__":
    web.run_app(app, port=PORT)