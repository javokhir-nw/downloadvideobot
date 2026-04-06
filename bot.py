import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import yt_dlp

# ================== CONFIG ==================
TOKEN = os.getenv("BOT_API")

if not TOKEN:
    raise ValueError("BOT_API environment variable topilmadi!")

print("TOKEN:", TOKEN)
print("Current dir:", os.getcwd())



# ================== LOGGING ==================
logging.basicConfig(level=logging.INFO)

# ================== INIT ==================
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# ================== YT-DLP FUNCTION ==================
def download_video(url: str) -> str:
    ydl_opts = {
    'outtmpl': '/tmp/%(title)s.%(ext)s',  # /tmp folder ishlatiladi
    'format': 'best',
    'noplaylist': True,
    'quiet': True,
    }

    os.makedirs("downloads", exist_ok=True)

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

# ================== HANDLERS ==================
@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "👋 Salom!\n\n"
        "Menga YouTube / TikTok / Instagram link yuboring.\n"
        "Men sizga videoni yuklab beraman 🎬"
    )

@dp.message()
async def download_handler(message: Message):
    url = message.text.strip()

    if not url.startswith("http"):
        await message.reply("❌ Iltimos, to‘g‘ri link yuboring.")
        return

    msg = await message.reply("⏳ Yuklanmoqda...")

    try:
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(None, download_video, url)

        file_size = os.path.getsize(file_path)

        # 50MB limit (Telegram oddiy upload)
        if file_size > 50 * 1024 * 1024:
            await msg.edit_text("⚠️ Video juda katta (50MB dan katta).")
            return

        await message.reply_video(
            video=types.FSInputFile(file_path),
            caption="✅ Yuklandi"
        )

        os.remove(file_path)

    except Exception as e:
        logging.error(e)
        await msg.edit_text("❌ Xatolik yuz berdi. Linkni tekshirib ko‘ring.")

# ================== MAIN ==================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())