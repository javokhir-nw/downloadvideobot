import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import ParseMode
from yt_dlp import YoutubeDL

# --- Environment variables ---
TOKEN = os.environ.get("BOT_API")  # Render-ga BOT_API sifatida qo'yish
PORT = int(os.environ.get("PORT", 8000))  # Render port

# ----- Minimal web server -----
async def handle(request):
    return web.Response(text="Bot ishlayapti ✅")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"Web server port {PORT}da ishga tushdi ✅")

# ----- Bot -----
async def start_bot():
    bot = Bot(token=TOKEN, default=types.DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    @dp.message()
    async def download_handler(message: types.Message):
        url = message.text.strip()
        if not url.startswith("http"):
            await message.reply("Iltimos, to‘g‘ri link yuboring.")
            return

        await message.reply("Yuklanmoqda... ⏳")
        try:
            ydl_opts = {
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'format': 'bestvideo+bestaudio/best',
                'noplaylist': True,
            }
            os.makedirs("downloads", exist_ok=True)
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                file_path = ydl.prepare_filename(info)
            await message.reply_document(open(file_path, "rb"))
        except Exception as e:
            await message.reply(f"Xatolik yuz berdi: {e}")

    print("Bot ishga tushdi ✅")
    await dp.start_polling(bot)

# ----- Main -----
async def main():
    # Web serverni fon ish sifatida ishga tushirish
    asyncio.create_task(start_web_server())
    # Bot ishga tushishi
    await start_bot()

if __name__ == "__main__":
    asyncio.run(main())